# 《戰鬥陀螺 X》(Beyblade X) 職業聯賽戰術教練 LINE 助手

全球頂尖《戰鬥陀螺 X》(Beyblade X) 職業聯賽戰術教練與改裝大師專用 LINE 助手。具備全量 BX/UX 部件資料庫、Gemini AI 驅動的四大維度專業拆解、科技感 LINE Flex Message 戰術戰報卡片，並隨附官方規格與部件參考圖片。

---

## 🌟 核心特色

1. **四維度深度戰術拆解**：
   - 💥 **攻擊力與極速突襲 (X-Dash) 觸發率**：齒輪咬合深度、首發進軌角度、衝刺路徑與 Over Finish 幾率。
   - 🌀 **持久力（旋轉時間）與尾速表現**：圓盤外圍配重離心效能、接地摩擦阻力、最後同轉勝負 (Spin Finish)。
   - 🛡️ **防禦力（抗擊飛、抗爆裂能力）**：墊片高度重心（60 vs 70 vs 80）、齒數分散受力（9-60 vs 5-60 vs 3-60）、防撬爆能力。
   - ⚔️ **主流熱門對戰勝率與克制關係**：深度評析對陣 Phoenix Wing、Wizard Rod、Dran Buster、Cobalt Dragoon 等賽事霸主之克制鏈。
2. **全量 BX/UX 部件數據圖鑑**：
   - 收錄 Phoenix Wing、Wizard Rod、Dran Buster、Cobalt Dragoon、Shark Edge、Silver Wolf 等全量刃部。
   - 包含 9-60、5-60、7-60、1-60、3-80、5-70 等墊片規格。
   - 包含 Ball、Orb、Flat、Taper、Point、Gear Flat、Free Ball 等全系列軸心。
3. **賽事轉播級 LINE Flex Message**：
   - 自動合成高科技戰報卡片、四維數據進度條、實體部件重量與官方參考圖片。
4. **雙模測試與快速部署**：
   - 本地終端 CLI 模擬器（不開 LINE 也能秒測對話與數據）。
   - Cloudflared 本地穿透腳本（一鍵生成 Webhook 公網 URL）。
   - 支援 Docker 與 Render 雲端一鍵託管。

---

## 📁 專案結構

```
beyblade-x-coach-bot/
├── data/
│   └── parts_db.json          # BX/UX 全量部件規格與官方圖床資料庫
├── core/
│   ├── database.py            # 部件檢索、物理數值計算與組合解析引擎
│   ├── coach_engine.py        # Gemini 戰術大腦與四大維度提示詞工程
│   └── flex_builder.py        # LINE Flex Message 戰術戰報與圖鑑卡生成器
├── web/
│   └── app.py                 # FastAPI Webhook Server (LINE Messaging API v3)
├── cli_tester.py              # 本地終端 CLI 戰術教練模擬器
├── run_tunnel.py              # Cloudflared 穿透自動化腳本
├── config.py                  # 全域環境變數組態
├── .env                       # 本地金鑰與 LINE 權杖配置
├── requirements.txt           # 專案依賴庫
└── Dockerfile                 # 容器化建置設定
```

---

## 🚀 快速開始

### 1. 安裝依賴
```powershell
pip install -r requirements.txt
```

### 2. 設定環境變數 (.env)
```env
LINE_CHANNEL_ACCESS_TOKEN=你的_LINE_Channel_Access_Token
LINE_CHANNEL_SECRET=你的_LINE_Channel_Secret
GEMINI_API_KEY=你的_Google_Gemini_API_Key
PORT=8000
HOST=0.0.0.0
```

### 3. 本地終端直接體驗 (CLI Tester)
無需架設伺服器即可直接與教練進行戰術研討：
```powershell
python cli_tester.py
```
> 輸入搭配範例：
> - `Phoenix Wing 9-60O`
> - `魔導權杖 7-60 B`
> - `Dran Buster 1-60F`
> - `9-60`

### 4. 啟動 LINE Webhook 伺服器
```powershell
python -m uvicorn web.app:app --reload --port 8000
```

### 5. 啟動 Cloudflared 本地穿透
在另一個終端執行：
```powershell
python run_tunnel.py
```
執行後終端將印出專屬的公網 Webhook URL（例如：`https://xxx.trycloudflare.com/callback`），將此網址複製並貼入 [LINE Developers Console](https://developers.line.biz/) 的 Webhook settings 即可！

---

## 🧪 執行自動化單元測試
```powershell
python -m unittest discover tests
```
涵蓋部件搜尋、物理運算、正則代號解析、Flex 卡片建構及 Gemini AI 戰術大腦的完整端到端測試。
