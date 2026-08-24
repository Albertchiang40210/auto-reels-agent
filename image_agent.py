from PIL import Image, ImageDraw, ImageFont
import os

def create_ig_post_image(title, subtitle, filename="ig_post.jpg"):
    """
    【Agent 3：視覺小編】負責把文字排版成 IG 圖片
    """
    print(f"\n[視覺小編] 收到設計需求，正在繪製圖片...")
    
    # 1. 建立一張 1080x1080 的正方形圖片 (IG 標準尺寸)，背景為深灰色
    img_size = (1080, 1080)
    background_color = (40, 42, 54) # 有質感的深色背景
    img = Image.new('RGB', img_size, color=background_color)
    draw = ImageDraw.Draw(img)
    
    # 2. 設定字體 (因為你是 Mac，我們使用內建的蘋方體)
    # 如果找不到字體，會拋出錯誤，你可以替換成其他中文字體路徑
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", 80)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", 40)
    except IOError:
        print("[錯誤] 找不到 Mac 內建中文字體，請確認字體路徑。")
        return

    # 3. 設定文字顏色
    text_color = (248, 248, 242) # 米白色文字
    accent_color = (255, 121, 198) # 粉色點綴
    
    # 4. 把大標題寫在中間偏上方
    # (簡單粗暴的固定座標排版，未來你可以學著寫置中對齊的邏輯)
    draw.text((100, 400), title, font=title_font, fill=text_color)
    
    # 5. 把副標題寫在大標題下方
    draw.text((100, 520), subtitle, font=subtitle_font, fill=accent_color)
    
    # 6. 在最底部加上小小的浮水印或帳號名稱
    footer_font = ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", 30)
    draw.text((100, 950), "@my_ai_agent_ig", font=footer_font, fill=(100, 100, 100))

    # 7. 儲存圖片
    img.save(filename)
    print(f"[視覺小編] 圖片已成功儲存為 👉 {filename}")

def main():
    print("🎨 歡迎來到 Visual Agent (視覺小編) 測試")
    
    # 假設這是從 Gemini (小編) 那裡產生出來的金句
    ai_title = "iPhone 17 Pro 上市了！"
    ai_subtitle = "效能攝影直接封頂，你想換嗎？"
    
    # 呼叫製圖函式
    create_ig_post_image(title=ai_title, subtitle=ai_subtitle, filename="test_post.jpg")

if __name__ == "__main__":
    main()
