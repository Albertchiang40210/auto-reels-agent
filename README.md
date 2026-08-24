# AI Content Factory (自動化 IG 圖影音智能體)

這是一個基於 Python 與 CrewAI 框架打造的「全自動社群內容產出系統」。只要輸入一個主題，系統就會自動上網查資料、撰寫文案、合成圖片，並透過微軟神經網路語音自動剪輯出包含配音的 MP4 短影音。

## 🌟 核心功能

*   **🔍 資料研究 (Search Agent)**：內建 DuckDuckGo 搜尋工具，自動抓取最新網路資訊。
*   **✍️ 內容創作 (Copywriter Agent)**：使用 Google Gemini 模型將生硬資料轉化為活潑的 IG 貼文與配音腳本，並確保以 JSON 格式精準輸出。
*   **🎨 視覺排版 (Visual Agent)**：利用 Pillow 自動產生 1080x1080 高質感知識圖卡。
*   **🎬 影音剪輯 (Video Agent)**：結合 `edge-tts` (微軟超逼真語音) 與 `moviepy`，一鍵全自動壓製 MP4 影片。
*   **🤖 企業級調度 (CrewAI)**：導入 CrewAI 多智能體框架，讓 Agent 之間自主協作、完美交接。

## 🛠️ 技術堆疊 (Tech Stack)

*   **語言**：Python 3
*   **AI 大腦**：Google Gemini (gemini-3.6-flash)
*   **Agent 框架**：CrewAI, LiteLLM
*   **影像與影音**：Pillow (PIL), MoviePy, edge-tts
*   **資料爬蟲**：DuckDuckGo Search (ddgs)

## 🚀 快速開始

1. 複製專案並安裝依賴套件：
   ```bash
   pip install -r requirements.txt
   ```
2. 建立 `.env` 檔案並填入你的 Gemini API Key：
   ```env
   GEMINI_API_KEY=你的金鑰
   ```
3. 執行終極整合版 Agent：
   ```bash
   python crew_agent.py
   ```
