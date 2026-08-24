import requests
import os
import time

def publish_to_instagram(video_path: str, caption: str):
    """
    真實的 Instagram Graph API 串接程式碼。
    注意：目前使用測試模式，若要實際上線，請填入合法的 ACCESS_TOKEN 與 IG_ACCOUNT_ID
    """
    print(f"\n[IG 發布模組] 收到任務，準備發布影片: {video_path}")
    print(f"[IG 發布模組] 貼文文案:\n{caption}\n")
    
    # ==========================================
    # 以下為串接 Meta API 所需的真實參數 (目前為空值，留給未來填寫)
    # ==========================================
    ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN_HERE")
    IG_ACCOUNT_ID = os.getenv("IG_ACCOUNT_ID", "YOUR_IG_ACCOUNT_ID_HERE")
    
    # 如果還沒有設定真實的金鑰，我們就跑「模擬發布流程」來做展示
    if ACCESS_TOKEN == "YOUR_ACCESS_TOKEN_HERE":
        print("⚠️ 系統偵測到尚未設定 Meta Access Token，進入【模擬發布測試模式】...")
        time.sleep(2)
        print("連線至 Instagram 伺服器...")
        time.sleep(1)
        print(f"上傳影片 {os.path.basename(video_path)}... (100%)")
        time.sleep(1)
        print("✅ 模擬發布成功！貼文已送出！\n")
        return True
        
    # ==========================================
    # 以下為真實的上傳邏輯 (需要合法 Token 才會執行成功)
    # ==========================================
    try:
        # 步驟 1: 建立 Media Container (將影片上傳到 IG 的暫存區)
        print("[API] 正在建立影片容器...")
        video_url = "https://your_hosted_video_url.com/video.mp4" # 實際上 IG API 需要一個公開網址來抓取影片
        media_url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": ACCESS_TOKEN
        }
        response = requests.post(media_url, data=payload)
        creation_id = response.json().get('id')
        
        # 步驟 2: 發布 Media Container
        print("[API] 正在正式發布到 Instagram...")
        publish_url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": ACCESS_TOKEN
        }
        publish_response = requests.post(publish_url, data=publish_payload)
        
        if publish_response.status_code == 200:
            print("✅ 成功發布到 Instagram！")
            return True
        else:
            print(f"❌ 發布失敗: {publish_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return False
