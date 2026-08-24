import os
from dotenv import load_dotenv
from google import genai
from ddgs import DDGS

# 載入環境變數與初始化 Gemini
load_dotenv()
client = genai.Client()

def search_web(query):
    """【工具】上網搜尋並回傳前 3 筆資料的純文字"""
    print(f"\n[研究員] 收到指令，正在上網搜尋: {query}...")
    results = ""
    try:
        with DDGS() as ddgs:
            search_generator = ddgs.text(query, region='wt-wt', safesearch='off', timelimit='y', max_results=3)
            for r in search_generator:
                results += f"標題: {r['title']}\n內文: {r['body']}\n\n"
    except Exception as e:
        print(f"[研究員] 搜尋失敗: {e}")
    return results

def researcher_agent(topic):
    """【Agent 1：資料收集員】負責上網找資料，並消化成重點報告"""
    raw_data = search_web(topic)
    
    print("[研究員] 搜尋完畢，正在撰寫內部研究報告...")
    system_prompt = "你是一個專業的資料分析師。請根據提供的搜尋資料，整理出 3 個最核心的重點，不要廢話，直接列點。"
    user_prompt = f"主題：{topic}\n原始資料：\n{raw_data}" if raw_data else f"請憑你的知識，整理出關於『{topic}』的3個重點。"
    
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[system_prompt, user_prompt]
    )
    return response.text

def copywriter_agent(topic, research_report):
    """【Agent 2：文案小編】負責根據研究報告，寫出 IG 貼文"""
    print("\n[小編] 收到研究報告，正在激盪腦力撰寫 IG 貼文...")
    system_prompt = "你是一個資深的 Instagram 行銷小編。請根據我提供的『研究報告』，寫出一篇吸引人的 IG 貼文，字數 150 字內，並加上適合的 Hashtag。語氣要活潑親切。"
    user_prompt = f"貼文主題：{topic}\n\n請務必參考以下研究報告來撰寫內容：\n{research_report}"
    
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[system_prompt, user_prompt]
    )
    return response.text

def main():
    print("🌟 歡迎來到 Agent 團隊協作系統 (自動化 IG 產出) 🌟")
    
    # 1. 取得老闆 (你) 的指令
    topic = input("👉 老闆你好，請問今天要發什麼主題的貼文呢？(例如：推薦3款超好用滑鼠)：")
    
    # 2. 呼叫研究員 (Agent 1)
    report = researcher_agent(topic)
    print("\n" + "="*15 + " 📝 研究員的內部報告 " + "="*15)
    print(report)
    print("="*50)
    
    # 3. 將報告交給小編 (Agent 2)
    ig_post = copywriter_agent(topic, report)
    print("\n" + "="*15 + " ✍️ 小編的最終貼文草稿 " + "="*15)
    print(ig_post)
    print("="*50)

if __name__ == "__main__":
    main()
