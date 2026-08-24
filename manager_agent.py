import os
import glob
import shutil
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

from ig_publisher import publish_to_instagram

load_dotenv()

# 初始化 Gemini 客戶端
client = genai.Client()

def generate_caption(topic: str) -> str:
    """讓 AI 擔任社群企劃，根據檔名(主題)自動想文案與語音腳本"""
    print(f"🧠 [AI 思考中] 正在為主題「{topic}」發想爆款 IG 貼文與配音...")
    
    prompt = f"""
    你現在是一位擁有百萬粉絲的 IG 社群經理。
    我剛剛剪好了一支關於「{topic}」的短影音。
    請幫我寫出一篇適合發在 Instagram 上的高互動性貼文內文，以及一段 20 秒內的短影音口白腳本。
    要求：
    1. 貼文前三句就要吸引人，加上適當的 Emoji，結尾要加上相關的 Hashtag (至少5個)。
    2. 口白腳本必須是極度口語化、像真人在說話的風格，並且把數字轉換成國字大寫發音以免念錯。
    
    請務必嚴格輸出為以下 JSON 格式 (不要包含 ```json 標籤，純輸出 JSON 字串)：
    {{
        "caption": "你的 IG 貼文內容...",
        "voice_script": "你的口語化配音腳本..."
    }}
    """
    
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt,
    )
    return response.text

def main():
    print("🚀 【全自動社群經理系統】啟動中...")
    
    draft_folder = "draft_videos"
    published_folder = "published_videos"
    
    # 確保資料夾存在
    os.makedirs(draft_folder, exist_ok=True)
    os.makedirs(published_folder, exist_ok=True)
    
    # 找尋草稿區有沒有待發布的 mp4 影片
    videos = glob.glob(os.path.join(draft_folder, "*.mp4"))
    
    if not videos:
        print("📭 目前草稿區沒有影片，社群經理繼續待機。")
        print(f"👉 請把你剪好的影片放到 {draft_folder}/ 資料夾中！")
        return
        
    print(f"👀 發現 {len(videos)} 支待發布影片！開始工作...")
    
    for video_path in videos:
        # 從檔名解析出「主題」 (例如: iPhone17爆料.mp4 -> iPhone17爆料)
        filename = os.path.basename(video_path)
        topic = os.path.splitext(filename)[0]
        
        print("\n" + "="*50)
        print(f"📌 開始處理影片: {filename}")
        
        # 1. 叫 AI 想文案
        caption = generate_caption(topic)
        
        # 2. 自動發送到 IG
        success = publish_to_instagram(video_path, caption)
        
        if success:
            # 發布成功後，把影片搬家到 published_videos 避免重複發布
            new_path = os.path.join(published_folder, filename)
            shutil.move(video_path, new_path)
            print(f"📦 影片已歸檔至: {published_folder}/")
            
        print("="*50)
        
        # 休息一下，避免連續發布被當作機器人或撞到 API Rate Limit
        time.sleep(5)

if __name__ == "__main__":
    main()
