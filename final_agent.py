import os
import json
from dotenv import load_dotenv
from google import genai
from ddgs import DDGS
from PIL import Image, ImageDraw, ImageFont

# 載入環境變數與初始化 Gemini
load_dotenv()
client = genai.Client()

def search_web(query):
    """【工具】上網搜尋並回傳資料"""
    print(f"[研究員] 正在上網搜尋: {query}...")
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
    """【Agent 1：資料收集員】"""
    raw_data = search_web(topic)
    print("[研究員] 搜尋完畢，正在撰寫重點報告...")
    system_prompt = "你是一個專業的資料分析師。請根據提供的搜尋資料，整理出 3 個最核心的重點，直接列點。"
    user_prompt = f"主題：{topic}\n原始資料：\n{raw_data}" if raw_data else f"請憑你的知識，整理出關於『{topic}』的3個重點。"
    
    response = client.models.generate_content(model="gemini-3.6-flash", contents=[system_prompt, user_prompt])
    return response.text

def copywriter_agent(topic, research_report):
    """【Agent 2：文案小編】輸出 JSON 格式"""
    print("[小編] 收到研究報告，正在撰寫貼文並構思圖片標題...")
    
    # 這是非常關鍵的一步：教 AI 輸出結構化的 JSON 格式！
    system_prompt = """你是一個資深的 Instagram 行銷小編。請根據提供的『研究報告』撰寫貼文。
    請務必嚴格使用 JSON 格式回傳，格式如下：
    {
        "image_title": "圖片上的大標題 (10字內)",
        "image_subtitle": "圖片上的副標題 (15字內)",
        "caption": "IG 貼文內文 (包含 Hashtag)"
    }
    """
    user_prompt = f"貼文主題：{topic}\n\n研究報告：\n{research_report}"
    
    # 我們可以利用 Google GenAI 的 response_schema 功能確保輸出是 JSON
    # 但為了讓新手容易理解，我們直接請 AI 輸出 JSON 字串，並在 Python 裡解析
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[system_prompt, user_prompt]
    )
    
    # 清理 AI 可能會加上的 ```json 標籤
    clean_text = response.text.replace("```json\n", "").replace("```", "").strip()
    return json.loads(clean_text)

def visual_agent(title, subtitle, filename="final_post.jpg"):
    """【Agent 3：視覺小編】繪製圖片"""
    print(f"[視覺小編] 收到文字，正在生成圖片: {filename}...")
    img = Image.new('RGB', (1080, 1080), color=(40, 42, 54))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", 80)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", 40)
        footer_font = ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", 30)
    except:
        print("[錯誤] 找不到字體")
        return

    draw.text((100, 400), title, font=title_font, fill=(248, 248, 242))
    draw.text((100, 520), subtitle, font=subtitle_font, fill=(255, 121, 198))
    draw.text((100, 950), "@my_ai_agent_ig", font=footer_font, fill=(100, 100, 100))

    img.save(filename)

def main():
    print("🚀 【終極大合體】一鍵產出圖文系統 🚀")
    topic = input("👉 請問今天要發什麼主題的貼文呢？：")
    
    # 1. 研究員找資料
    report = researcher_agent(topic)
    
    # 2. 小編寫 JSON
    try:
        post_data = copywriter_agent(topic, report)
        print("\n" + "="*15 + " ✍️ 小編的最終貼文 " + "="*15)
        print(post_data['caption'])
        print("="*45)
        
        # 3. 視覺小編做圖 (自動帶入小編想好的標題)
        visual_agent(post_data['image_title'], post_data['image_subtitle'])
        print("\n🎉 全部完成！快去看看 final_post.jpg 吧！")
        
    except Exception as e:
        print(f"❌ 發生錯誤 (可能是 AI 沒有乖乖輸出 JSON): {e}")

if __name__ == "__main__":
    main()
