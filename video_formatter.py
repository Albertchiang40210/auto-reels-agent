from moviepy import VideoFileClip, ColorClip, CompositeVideoClip, AudioFileClip
import os

def format_video_for_ig_reels(input_path: str, output_path: str, audio_path: str = None):
    """
    將影片轉換為 IG Reels 標準規格 (1080x1920, 9:16, 最長 90 秒)
    若傳入 audio_path，將覆寫影片的原始音軌。
    """
    print(f"🎬 [影片格式化] 開始處理影片: {input_path}")
    
    # 目標 IG Reels 規格
    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920
    MAX_DURATION = 90.0 # Reels 最長 90 秒
    
    try:
        # 讀取原始影片
        clip = VideoFileClip(input_path)
        
        # 1. 檢查並截斷影片長度 (超過 90 秒的部分切掉)
        if clip.duration > MAX_DURATION:
            print(f"⚠️ 影片長度 {clip.duration} 秒超過 Reels 限制，將自動裁切至 90 秒。")
            clip = clip.subclipped(0, MAX_DURATION)
            
        # 2. 計算縮放比例以符合 1080x1920 (保持原始比例，多餘部分補黑邊)
        # 我們將影片縮放，使其寬度=1080 或 高度=1920，且不超出範圍
        clip_ratio = clip.w / clip.h
        target_ratio = TARGET_WIDTH / TARGET_HEIGHT
        
        if clip_ratio > target_ratio:
            # 影片比較「寬」，所以寬度對齊 1080，高度按比例縮小
            resized_clip = clip.resized(width=TARGET_WIDTH)
        else:
            # 影片比較「高」，所以高度對齊 1920，寬度按比例縮小
            resized_clip = clip.resized(height=TARGET_HEIGHT)
            
        # 3. 建立 1080x1920 的純黑底色背景
        background = ColorClip(size=(TARGET_WIDTH, TARGET_HEIGHT), color=(0,0,0)).with_duration(clip.duration)
        
        # 4. 將縮放後的影片置中貼在黑底上 (自動置中，上下或左右會補黑邊)
        final_clip = CompositeVideoClip([background, resized_clip.with_position("center")])
        
        # 加入 AI 配音 (如果有)
        new_audio = None
        if audio_path and os.path.exists(audio_path):
            print("🔊 [音訊處理] 正在將 AI 語音合成至影片中...")
            new_audio = AudioFileClip(audio_path)
            # 如果音檔比影片短，直接套用；如果音檔比影片長，截斷音檔
            if new_audio.duration > final_clip.duration:
                new_audio = new_audio.subclipped(0, final_clip.duration)
            final_clip = final_clip.with_audio(new_audio)
        
        # 5. 輸出符合 IG 業界標準的 H.264 mp4 影片
        print("⚙️ 正在轉換為 IG 相容的 H.264 / AAC 編碼格式...")
        final_clip.write_videofile(
            output_path,
            fps=30, # 標準幀率
            codec="libx264", # IG 強制要求的 H.264 影像編碼
            audio_codec="aac", # IG 強制要求的 AAC 音訊編碼
            logger=None # 隱藏 moviepy 的複雜進度條以保持終端機乾淨
        )
        
        # 釋放記憶體
        clip.close()
        resized_clip.close()
        final_clip.close()
        if new_audio:
            new_audio.close()
        
        print(f"✅ 影片格式化完成！標準版影片已儲存至: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ 影片格式化失敗: {e}")
        return False
