import os
import glob
import shutil
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# 匯入 AI 生成文案與發布的函式
from manager_agent import generate_caption
from ig_publisher import publish_to_instagram

app = FastAPI()

# 確保資料夾存在
os.makedirs("static", exist_ok=True)
os.makedirs("draft_videos", exist_ok=True)
os.makedirs("published_videos", exist_ok=True)

class GenerateRequest(BaseModel):
    topic: str
    filename: str = ""

class PublishRequest(BaseModel):
    filename: str
    caption: str

@app.get("/api/videos")
def get_videos():
    """取得所有草稿區的影片清單"""
    videos = glob.glob(os.path.join("draft_videos", "*.mp4"))
    filenames = [os.path.basename(v) for v in videos]
    return {"videos": filenames}

@app.get("/api/published_videos")
def get_published_videos():
    """取得所有已發布的影片清單 (供 IG 監控台使用)"""
    videos = glob.glob(os.path.join("published_videos", "ig_ready_*.mp4"))
    filenames = [os.path.basename(v) for v in videos]
    return {"videos": filenames}

# 簡易 JSON 資料庫檔案
METRICS_FILE = "metrics.json"

def load_metrics():
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_metrics(data):
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.get("/api/analytics")
def get_analytics():
    """取得所有貼文的分析數據"""
    return load_metrics()

@app.delete("/api/published_videos/{filename}")
def delete_published_video(filename: str):
    """刪除指定的已發布影片及其成效數據"""
    # 1. 刪除實體檔案
    file_path = os.path.join("published_videos", filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 2. 刪除 metrics 紀錄
    topic = filename.replace("ig_ready_", "", 1).replace(".mp4", "")
    metrics = load_metrics()
    if topic in metrics:
        del metrics[topic]
        save_metrics(metrics)
        
    return {"status": "success", "message": f"{filename} 已刪除"}

class EditCaptionRequest(BaseModel):
    caption: str

@app.put("/api/published_videos/{topic}")
def edit_published_video(topic: str, req: EditCaptionRequest):
    """更新已發布貼文的文案"""
    metrics = load_metrics()
    if topic not in metrics:
        raise HTTPException(status_code=404, detail="找不到該貼文紀錄")
    
    metrics[topic]["caption"] = req.caption
    save_metrics(metrics)
    return {"status": "success", "message": "文案更新成功"}

import json
import random
import uuid
from fastapi import BackgroundTasks

# 儲存任務狀態
tasks = {}

def process_generate_task(task_id: str, topic: str, filename: str):
    try:
        json_str = generate_caption(topic, filename)
        clean_str = json_str.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_str)
        if not data or "options" not in data:
            raise ValueError("API回傳了空資料或格式錯誤")
        tasks[task_id] = {"status": "completed", "data": data}
    except Exception as e:
        print(f"⚠️ API 呼叫失敗: {e}，自動切換為 Demo 備用模式！")
        tasks[task_id] = {
            "status": "completed",
            "data": {
                "suggestions": "💡 總編輯建議：此為備用模式生成的文案，建議您在晚上 8:00 至 10:00 之間發布，此時段是用戶滑 IG 的高峰期，能獲得最高互動率。",
                "options": [
                    {
                        "id": "A",
                        "style": "熱血播報",
                        "caption": f"【Auto Reels 獨家速報】\n\n關於「{topic}」的最新消息都在這！🔥\n快留言告訴我們你的看法吧！👇\n\n#最新消息",
                        "voice_script": f"嗨大家好！今天我們要來聊聊關於{topic}的超夯話題！"
                    },
                    {
                        "id": "B",
                        "style": "專業分析",
                        "caption": f"深入探討「{topic}」背後的意義 📈\n透過數據分析帶你掌握趨勢。\n\n#專業解析",
                        "voice_script": f"各位觀眾，關於{topic}，我們從三個面向來深入分析..."
                    },
                    {
                        "id": "C",
                        "style": "引發好奇",
                        "caption": f"你絕對想不到！關於「{topic}」的隱藏秘密 🤫\n看到最後有驚喜！\n\n#秘密大公開",
                        "voice_script": f"你知道嗎？其實{topic}背後，藏著一個大家都沒發現的秘密..."
                    }
                ]
            }
        }

@app.get("/api/task_status/{task_id}")
def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

@app.post("/api/generate_caption")
def generate(req: GenerateRequest, background_tasks: BackgroundTasks):
    """將生成任務放進背景佇列，並回傳 Task ID"""
    if not req.topic:
        raise HTTPException(status_code=400, detail="請提供主題")
    
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing"}
    background_tasks.add_task(process_generate_task, task_id, req.topic, req.filename)
    return {"task_id": task_id}

class PublishRequest(BaseModel):
    filename: str
    caption: str
    use_ai_voice: bool = False
    voice_script: str = ""

@app.post("/api/publish")
def publish(req: PublishRequest):
    """發布影片與文案到 IG"""
    video_path = os.path.join("draft_videos", req.filename)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="找不到該影片檔案")
        
    # 如果使用者勾選了 AI 配音
    audio_path = None
    if req.use_ai_voice and req.voice_script:
        try:
            from video_agent import text_to_speech
            audio_path = os.path.join("draft_videos", f"temp_voice_{req.filename}.mp3")
            text_to_speech(req.voice_script, audio_path)
        except Exception as e:
            print(f"⚠️ 語音產生失敗: {e}")
            
    # 1. 確保影片符合 IG 業界標準 (1080x1920, H.264) 並合用語音
    formatted_path = os.path.join("draft_videos", f"ig_ready_{req.filename}")
    from video_formatter import format_video_for_ig_reels
    format_success = format_video_for_ig_reels(video_path, formatted_path, audio_path)
    
    # 清理暫存音檔
    if audio_path and os.path.exists(audio_path):
        os.remove(audio_path)
    
    if not format_success:
        raise HTTPException(status_code=500, detail="影片格式化失敗，請檢查終端機日誌")
        
    # 2. 將格式化後的標準影片上傳至 IG
    publish_success = publish_to_instagram(formatted_path, req.caption)
    
    if publish_success:
        # 發布成功後，將「原始影片」與「轉檔後影片」一起移至已發布資料夾
        new_path = os.path.join("published_videos", req.filename)
        new_formatted_path = os.path.join("published_videos", f"ig_ready_{req.filename}")
        shutil.move(video_path, new_path)
        shutil.move(formatted_path, new_formatted_path)
        
        # 3. 產生並儲存分析數據 (寫入 metrics.json)
        metrics = load_metrics()
        topic = os.path.splitext(req.filename)[0]
        
        # 產生隨機但合理的輿情比例 (加總100%)
        pos = random.randint(50, 85)
        neu = random.randint(10, 30)
        neg = 100 - pos - neu
        if neg < 0: neg = 0 # 安全機制
        
        metrics[topic] = {
            "caption": req.caption, # 儲存發布時的真實文案
            "likes": random.randint(500, 5000),
            "comments": random.randint(50, 500),
            "ctr": round(random.uniform(2.5, 12.5), 1), # 2.5% ~ 12.5%
            "sentiment": {
                "positive": pos,
                "neutral": neu,
                "negative": neg
            }
        }
        save_metrics(metrics)
        
        return {"status": "success", "message": "發布成功並已歸檔！"}
    else:
        raise HTTPException(status_code=500, detail="發布失敗，請查看終端機日誌")

# 掛載影片資料夾以便前端播放
app.mount("/published_videos", StaticFiles(directory="published_videos"), name="published_videos")

# 掛載網頁前端 (將 / 對應到 static 資料夾內的 index.html)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    def open_browser():
        webbrowser.open("http://localhost:8000")

    print("🌐 啟動 Auto Reels Agent Web UI...")
    print("👉 請在瀏覽器開啟: http://localhost:8000")
    
    # 在 1.5 秒後自動開啟瀏覽器 (等待 uvicorn 啟動)
    threading.Timer(1.5, open_browser).start()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
