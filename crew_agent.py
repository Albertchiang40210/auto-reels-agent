import os
import json
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from ddgs import DDGS
from pydantic import BaseModel, Field

# 匯入我們之前寫好的好用小工具！
from final_agent import visual_agent
from video_agent import text_to_speech, create_video_from_image_and_audio

load_dotenv()

# 設定 CrewAI 使用的 LLM (因為你目前的帳號權限，我們需指定使用 3.6-flash 版本)
gemini_llm = LLM(model="gemini/gemini-3.6-flash")

# ==========================================
# 1. 定義自訂工具 (Tools)
# ==========================================
@tool("DuckDuckGo Web Search")
def web_search_tool(query: str) -> str:
    """用來上網搜尋最新資料的工具，請傳入想要搜尋的關鍵字。"""
    print(f"\n[系統提示] 研究員正在使用搜尋工具查資料: {query}...")
    results = ""
    try:
        with DDGS() as ddgs:
            search_generator = ddgs.text(query, region='wt-wt', safesearch='off', timelimit='y', max_results=3)
            for r in search_generator:
                results += f"標題: {r['title']}\n內文: {r['body']}\n\n"
    except Exception as e:
        return f"搜尋失敗: {e}"
    return results

# ==========================================
# 2. 結構化輸出定義 (Pydantic Model)
# ==========================================
class IGPostOutput(BaseModel):
    image_title: str = Field(description="圖片上的大標題 (10字內)")
    image_subtitle: str = Field(description="圖片上的副標題 (15字內)")
    caption: str = Field(description="IG 貼文內文 (包含 Hashtag)")
    voice_script: str = Field(description="給配音員唸的口語化短影音腳本，數字必須轉換為國字寫法以免唸錯")

# ==========================================
# 3. 定義員工 (Agents) - 拔除網路搜尋，改為內部企劃
# ==========================================
strategist = Agent(
    role='首席內容企劃',
    goal='根據老闆給的指示 {topic}，憑藉你的專業知識與創意，發想出 3 個最具吸引力的貼文重點。',
    backstory='你是一位在社群行銷界打滾多年的金牌企劃，不需要上網查資料，你的腦袋裡就有滿滿的創意與爆款點子。',
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)

copywriter = Agent(
    role='爆款 IG 行銷小編',
    goal='根據企劃提供的重點，寫出能吸引年輕人的 IG 圖文內容與短影音腳本',
    backstory='你是一個精通社群病毒行銷的小編，知道怎麼下標題最吸睛，也知道配音腳本怎麼寫最自然。',
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)

# ==========================================
# 4. 定義任務 (Tasks)
# ==========================================
strategy_task = Task(
    description='根據老闆的主題 {topic}，腦力激盪並規劃出 3 個最能引起網友共鳴的切入點與核心重點。',
    expected_output='一份條理分明的 3 點企劃大綱。',
    agent=strategist
)

write_task = Task(
    description='根據企劃提供的大綱，撰寫一則 IG 貼文，並構思圖片上的主副標題。同時，寫一段長度約 20 秒內的口語化短影音配音腳本。',
    expected_output='一段完美的 IG 貼文內容以及影音腳本。',
    agent=copywriter,
    output_pydantic=IGPostOutput # 強制要求 AI 輸出我們定義好的結構！
)

# ==========================================
# 5. 啟動團隊 (Crew) 供外部呼叫
# ==========================================
def run_crew(topic: str):
    print(f"🚀 【CrewAI 企業級架構】開始處理主題: {topic}")
    
    # 建立團隊，把員工和任務放進去
    my_crew = Crew(
        agents=[strategist, copywriter],
        tasks=[strategy_task, write_task],
        process=Process.sequential # 循序漸進：做完企劃再寫文案
    )
    
    # 開始工作！(會自動帶入 {topic} 變數)
    print("\n" + "="*50)
    result = my_crew.kickoff(inputs={'topic': topic})
    print("="*50 + "\n")
    
    # 取得結構化的結果 (因為我們有設定 output_pydantic)
    post_data = result.pydantic
    
    print("\n✅ CrewAI 策劃完畢！正在交由自動化產線製作圖影...\n")
    
    # 6. 自動化產線：做圖 -> 配音 -> 剪片
    video_filename = "crew_video.mp4"
    try:
        # 做圖
        visual_agent(post_data.image_title, post_data.image_subtitle, "crew_post.jpg")
        
        # 配音 (已經被 AI 轉換過國字發音的腳本)
        audio_file = text_to_speech(post_data.voice_script, "crew_voice.mp3")
        
        # 剪片
        create_video_from_image_and_audio("crew_post.jpg", audio_file, video_filename)
        
        print(f"\n🎉 全部大功告成！請查看你的 {video_filename} 吧！")
        
        return {
            "status": "success",
            "caption": post_data.caption,
            "video_url": f"/{video_filename}"
        }
    except Exception as e:
        print(f"❌ 產線發生錯誤: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    print("🚀 歡迎來到 Auto Reels Agent CLI")
    topic = input("👉 老闆你好，請問今天要發什麼主題的貼文呢？：")
    run_crew(topic)
