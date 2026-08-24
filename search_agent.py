import os
from dotenv import load_dotenv
from google import genai
from ddgs import DDGS

# 1. 載入環境變數與初始化 Gemini
load_dotenv()
client = genai.Client()

def search_web(query):
    """這個函式負責上網搜尋，並回傳整理好的文字"""
    print(f"🔍 正在上網搜尋: {query}...")
    results = ""
    # 使用 DDGS 搜尋前 3 筆結果
    with DDGS() as ddgs:
        # text 搜尋會回傳一個 generator，我們取前 3 個結果
        search_generator = ddgs.text(query, region='wt-wt', safesearch='off', timelimit='y', max_results=3)
        for r in search_generator:
            results += f"標題: {r['title']}\n"
            results += f"內文: {r['body']}\n"
            results += f"連結: {r['href']}\n\n"
    return results

def main():
    print("🕵️‍♂️ 歡迎來到 Researcher Agent (資料收集員) 測試")
    
    # 讓使用者可以自己輸入想讓 AI 研究的主題
    topic = input("👉 請輸入你想讓 AI 幫你搜尋研究的主題 (例如：2024 最新皮膚保養趨勢)：")
    
    # 1. 讓 Agent 去上網搜尋
    search_data = search_web(topic)
    print("✅ 搜尋完成！找到以下原始資料：")
    print("-" * 30)
    print(search_data)
    print("-" * 30)
    
    # 2. 將搜尋到的資料交給 AI (大腦) 進行整理與摘要
    system_prompt = "你是一個專業的資料分析師。請根據我提供的網路搜尋資料，整理出 3 個最核心的重點，並用繁體中文列點說明。如果資料不足，請就現有資料盡量統整。"
    user_prompt = f"搜尋主題：{topic}\n\n搜尋到的原始資料如下：\n{search_data}"
    
    print("\n🧠 正在將資料交給 AI 整理重點...")
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[system_prompt, user_prompt]
        )
        print("\n====== 📝 AI 整理的研究報告 ======\n")
        print(response.text)
        print("\n===================================")
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")

if __name__ == "__main__":
    main()
