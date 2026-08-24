# Auto Reels Agent (企業級 AI 社群營運系統) 🚀

這是一套為「現代社群小編與行銷團隊」量身打造的 **企業級 AI 社群營運 SaaS 軟體**。
有別於傳統的全自動爬蟲發文機，本系統強調 **「Human-in-the-Loop (人機協作)」** 與 **「視覺化數據監控」**，提供最安全、最具質感的社群發布體驗。

## 🌟 系統亮點 (核心功能)

*   **🔐 企業級權限控管 (Login Wall)**
    *   內建高質感的登入畫面，必須持有管理員密碼才能解鎖控制台，確保社群帳號安全。
*   **🧠 AI 雙核智能發想 (Gemini x TTS)**
    *   自動偵測待發布的短影音，呼叫 **Google Gemini** 自動產出「高互動 IG 貼文」與「口語化配音腳本」。
    *   支援一鍵開啟 **微軟 TTS (曉辰)** 語音合成，自動為影片配音。
*   **🛡️ IG 業界標準轉檔 (Video Formatter)**
    *   底層整合 `moviepy`，在發布前強制將任何格式的影片裁切/縮放為 **1080x1920 (9:16) 最佳比例** 與 H.264 編碼，確保 IG 原廠 API 100% 接收成功。
*   **📱 雙螢幕即時監控台 (Split-Screen Dashboard)**
    *   突破 Instagram 原廠禁止 iframe 的限制，自建 **Meta Graph API 模擬監控中心**。
    *   發布成功後，右側面板會立刻同步最新貼文，並模擬粉絲真實互動留言。
*   **📈 商業智慧分析中心 (BI Analytics)**
    *   不需依賴笨重的大型資料庫，採用輕量級 `JSON File-based DB`。
    *   整合 **Chart.js** 繪製高品質的三大圖表：
        1. **雙色長條圖 (Bar Chart)**：比較各貼文按讚與留言數。
        2. **點擊率折線圖 (Line Chart)**：追蹤流量趨勢。
        3. **輿情分析甜甜圈圖 (Sentiment Doughnut)**：AI 自動判讀留言風向 (好評/中立/負評)，形成完整行銷鐵三角。

## 🛠️ 技術堆疊 (Tech Stack)

*   **後端框架**：FastAPI, Python 3
*   **AI 大腦**：Google Gemini (gemini-3.6-flash)
*   **前端介面**：HTML5, CSS3 (Glassmorphism + IG Marketing Aesthetic), Vanilla JS
*   **資料庫**：JSON File-based DB (`metrics.json`)
*   **影音處理**：MoviePy, edge-tts
*   **資料視覺化**：Chart.js

## 🚀 快速開始 (Quick Start)

### 1. 安裝環境與依賴套件
```bash
# 建議使用虛擬環境
pip install -r requirements.txt
```

### 2. 環境變數設定
建立一個 `.env` 檔案並填入你的 Gemini API Key：
```env
GEMINI_API_KEY=你的金鑰
```

### 3. 準備影片草稿
在專案根目錄下建立 `draft_videos` 資料夾，並放入你剪接好的 `.mp4` 影片（檔名會自動作為 AI 發想的主題，例如 `iPhone17爆料.mp4`）。

### 4. 啟動伺服器
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
啟動後，請打開瀏覽器前往 👉 `http://localhost:8000`
（預設登入密碼為：`admin123`）

---
*專為期末專題打造的頂級火力展示，完美詮釋 AI 與商業營運的結合。*
