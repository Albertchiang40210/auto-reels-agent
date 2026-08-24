import os
from dotenv import load_dotenv
from google import genai

# 1. 載入 .env 檔案中的環境變數 (例如 API Key)
load_dotenv()

# 2. 建立 Gemini 客戶端
# 系統會自動去環境變數中尋找 GEMINI_API_KEY
client = genai.Client()

def main():
    print("🤖 歡迎來到你的 AI 小編系統！(使用 Gemini 引擎)")
    
    # 這是我們要給 AI 的「任務提示」(Prompt)
    system_prompt = "你是一個資深的 Instagram 行銷小編，擅長寫出吸引人的貼文。請在 100 字內完成任務，並加上適合的 Hashtag。"
    
    # 讓使用者可以自己輸入想要的主題
    user_topic = input("👉 請輸入你想寫的 IG 貼文主題 (例如：推廣每天喝水)：")
    user_prompt = f"請幫我寫一篇推廣『{user_topic}』的 IG 貼文。"
    
    print(f"\n正在請 AI 撰寫貼文...\n主題: {user_prompt}\n")

    # 3. 呼叫 Gemini API
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash", # 使用目前最新的 gemini-3.6-flash
            contents=[system_prompt, user_prompt]
        )

        # 4. 印出 AI 的回覆
        ai_reply = response.text
        print("====== ✍️ AI 小編產出的草稿 ======\n")
        print(ai_reply)
        print("\n===================================")
        
    except Exception as e:
        print(f"❌ 發生錯誤，請確認你是否已經將 API Key 貼入 .env 檔案中？\n詳細錯誤訊息: {e}")

if __name__ == "__main__":
    main()
