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

import json
from ddgs import DDGS

def get_web_info(topic: str) -> str:
    print(f"🔍 [Web Search] 正在搜尋關於「{topic}」的最新資訊...")
    try:
        results = DDGS().text(topic, max_results=3)
        if not results: return "無搜尋結果"
        info = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        return info
    except Exception as e:
        print(f"⚠️ 搜尋失敗: {e}")
        return "無法取得最新資訊"

def get_memory_info() -> str:
    print(f"🧠 [Memory] 讀取歷史發文成效...")
    try:
        if os.path.exists("metrics.json"):
            with open("metrics.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            if data:
                # 找出按讚數最高的貼文主題
                best_topic = max(data.keys(), key=lambda k: data[k].get("likes", 0))
                best_likes = data[best_topic].get("likes", 0)
                return f"歷史最佳表現貼文為「{best_topic}」，獲得 {best_likes} 個讚。請參考這種受歡迎的主題風格來撰寫。"
    except Exception as e:
        print(f"⚠️ 讀取記憶失敗: {e}")
    return "尚無足夠的歷史發文數據可供參考。"

def generate_caption(topic: str, filename: str = "") -> str:
    """讓 AI 擔任社群企劃，進行搜尋、看片、發想與總編審核"""
    print(f"🚀 [Agent 啟動] 開始處理主題「{topic}」...")
    
    # 1. 外部工具 (Tool Use): 搜尋最新資訊
    web_info = get_web_info(topic)
    
    # 2. 歷史記憶 (Memory): 讀取過去最佳表現
    memory_info = get_memory_info()
    
    contents = []
    video_path = os.path.join("draft_videos", filename) if filename else ""
    uploaded_video = None
    
    # 3. Vision 能力: 上傳影片
    if video_path and os.path.exists(video_path):
        print(f"👁️ [AI 審片中] 正在觀看影片: {filename} ...")
        temp_ascii_path = f"temp_{uuid.uuid4().hex}.mp4"
        try:
            import shutil
            shutil.copy(video_path, temp_ascii_path)
            uploaded_video = client.files.upload(file=temp_ascii_path)
            contents.append(uploaded_video)
            os.remove(temp_ascii_path)
        except Exception as e:
            print(f"⚠️ 影片上傳失敗: {e}")
            if os.path.exists(temp_ascii_path):
                os.remove(temp_ascii_path)
            
    # 4. Agent A + B 聯合發想 (單次呼叫以提高穩定性並確保 JSON 結構)
    print(f"✍️ [Multi-Agent 討論中] 創作者與總編輯正在激盪想法...")
    prompt = f"""
    你們是一個頂尖的 IG 行銷團隊，包含「創作者」與「總編輯」。
    今天的主題是：「{topic}」。
    
    【網路最新資訊】
    {web_info}
    
    【歷史成效反饋】
    {memory_info}
    
    請依照上述資訊，以及{"隨附的影片內容" if uploaded_video else "主題"}, 完成以下任務：
    1. 創作者需撰寫 3 個不同風格的貼文草稿與 20 秒短語音腳本 (數字用國字大寫)。
    2. 總編輯需根據網路資訊與歷史成效，給出「發布與優化建議」。
    
    請務必嚴格輸出為以下 JSON 格式 (不要包含 ```json 標籤，純輸出 JSON 字串)：
    {{
        "suggestions": "總編輯的整體發布與優化建議...",
        "options": [
            {{
                "id": "A",
                "style": "風格名稱 (例如: 幽默搞笑)",
                "caption": "貼文內容...",
                "voice_script": "配音腳本..."
            }},
            {{
                "id": "B",
                "style": "風格名稱...",
                "caption": "貼文內容...",
                "voice_script": "配音腳本..."
            }},
            {{
                "id": "C",
                "style": "風格名稱...",
                "caption": "貼文內容...",
                "voice_script": "配音腳本..."
            }}
        ]
    }}
    """
    contents.append(prompt)
    
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=contents,
        )
        result = response.text
    except Exception as e:
        print(f"⚠️ API 呼叫失敗: {e}")
        result = "{}"
        
    # 清理雲端檔案
    if uploaded_video:
        try:
            client.files.delete(name=uploaded_video.name)
        except Exception:
            pass
            
    return result

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
