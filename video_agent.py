import os
from moviepy import ImageClip, AudioFileClip
from PIL import Image, ImageDraw, ImageFont

def text_to_speech(text, audio_filename="voice.mp3"):
    """使用 Edge TTS (微軟神經網路語音) 將文字轉成超逼真語音檔案"""
    print("[配音小編] 正在錄製超逼真口白...")
    # zh-TW-HsiaoChenNeural 是微軟 Azure 提供的超逼真台灣女聲
    # 我們改用 .venv 裡面的 edge-tts 絕對路徑，避免找不到指令
    command = f'.venv/bin/edge-tts --text "{text}" --write-media "{audio_filename}" --voice zh-TW-HsiaoChenNeural'
    os.system(command)
    return audio_filename

def create_video_from_image_and_audio(image_path, audio_path, output_filename="final_video.mp4"):
    """將靜態圖片與語音結合，產生 MP4 影片"""
    print("[剪輯小編] 正在合成影片...")
    
    # 1. 載入語音檔
    audio_clip = AudioFileClip(audio_path)
    
    # 2. 載入圖片，並將圖片顯示的時間長度設定為「跟語音一樣長」
    image_clip = ImageClip(image_path).with_duration(audio_clip.duration)
    
    # 3. 將圖片與聲音結合
    video = image_clip.with_audio(audio_clip)
    
    # 4. 輸出成 MP4 檔案 (fps=24 即可，因為是靜態圖)
    video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
    print(f"\n🎉 影片剪輯完成！請查看 👉 {output_filename}")

def main():
    print("🎬 歡迎來到 Video Agent (影音小編) 測試")
    
    # 假設這是我們要發布的短影音腳本
    script = "顯卡界的新帝王降臨！RTX 5090 實測報告出爐，效能輕鬆輾壓上一代，你準備好升級你的配備了嗎？"
    
    # 💡【語音處理小技巧】：TTS 引擎常會把數字唸成「幾千幾百」，我們可以寫一段程式把它替換掉！
    # 將 5090 換成 "五零九零" 確保發音正確
    speech_text = script.replace("5090", "五零九零")
    
    # 1. 產生語音檔 (傳入修改過發音的 speech_text)
    audio_file = text_to_speech(speech_text, "voice.mp3")
    
    # 2. 我們直接拿剛剛做好的 test_post.jpg 或 final_post.jpg 當作背景圖
    # (請確保目錄下有這個檔案，否則會報錯)
    bg_image = "final_post.jpg"
    
    if not os.path.exists(bg_image):
        print(f"❌ 找不到背景圖 {bg_image}，請先執行 final_agent.py 產生圖片！")
        return

    # 3. 合成影片
    create_video_from_image_and_audio(bg_image, audio_file, "final_video.mp4")

if __name__ == "__main__":
    main()
