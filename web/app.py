import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Header, BackgroundTasks
from pathlib import Path
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

from config import settings
from core.database import db
from core.coach_engine import coach_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("web.app")

line_webhook_handler = None
line_messaging_api = None

# Initialize LINE SDK v3 if credentials are provided
if settings.LINE_CHANNEL_SECRET and settings.LINE_CHANNEL_ACCESS_TOKEN:
    try:
        from linebot.v3 import WebhookHandler
        from linebot.v3.messaging import (
            Configuration,
            ApiClient,
            MessagingApi,
            ReplyMessageRequest,
            TextMessage,
            FlexMessage,
            FlexContainer
        )
        from linebot.v3.webhooks import MessageEvent, TextMessageContent

        line_webhook_handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)
        configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)

        @line_webhook_handler.add(MessageEvent, message=TextMessageContent)
        def handle_text_message(event):
            user_msg = event.message.text.strip()
            logger.info(f"Received message from user: {user_msg}")
            
            result = coach_engine.analyze(user_msg)
            reply_messages = []

            # 1. Add Flex Message card if combo or part was recognized
            if result.get("flex_message"):
                try:
                    flex_payload = result["flex_message"]
                    container = FlexContainer.from_dict(flex_payload["contents"])
                    reply_messages.append(
                        FlexMessage(
                            alt_text=flex_payload.get("altText", "戰鬥陀螺 X 戰報"),
                            contents=container
                        )
                    )
                except Exception as flex_err:
                    logger.error(f"Error packing Flex Message: {flex_err}")

            # 2. Add full detailed coach analysis text
            text_body = result.get("reply_text") or "選手，戰術分析完成。"
            reply_messages.append(TextMessage(text=text_body))

            with ApiClient(configuration) as api_client:
                line_bot = MessagingApi(api_client)
                line_bot.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=reply_messages
                    )
                )
            logger.info("Replied successfully to LINE user.")

        logger.info("LINE Webhook Handler and Messaging API successfully initialized.")
    except Exception as e:
        logger.warning(f"LINE SDK initialization warning: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Loaded {len(db.blades)} blades, {len(db.ratchets)} ratchets, {len(db.bits)} bits into registry.")

    # 雲端自動綁定：若在 Render 等雲端平台運行，啟動時自動向 LINE 官方回報 Webhook 網址，免手動設定！
    import os
    external_url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("SERVICE_URL")
    if external_url and settings.LINE_CHANNEL_ACCESS_TOKEN:
        try:
            clean_url = external_url.strip().rstrip("/")
            webhook_url = f"{clean_url}/callback"
            logger.info(f"檢測到雲端部署環境！正在全自動綁定 LINE Webhook: {webhook_url} ...")
            import requests
            res = requests.put(
                "https://api.line.me/v2/bot/channel/webhook/endpoint",
                headers={
                    "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={"endpoint": webhook_url},
                timeout=10
            )
            if res.status_code == 200:
                logger.info(f"🎉 LINE Webhook 全自動綁定成功: {webhook_url}")
            else:
                logger.warning(f"LINE Webhook 綁定回傳: {res.status_code} - {res.text}")
        except Exception as e:
            logger.warning(f"LINE Webhook 自動綁定失敗: {e}")

    yield

app = FastAPI(title="Beyblade X Tactical Coach LINE Bot", lifespan=lifespan)

LANDING_HTML = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>戰鬥陀螺 X 職業聯賽戰術教練 | 24H 雲端整備區</title>
    <link href="https://fonts.googleapis.com/css2?family=Teko:wght@600;700&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0A0D14;
            --card-bg: rgba(19, 24, 34, 0.85);
            --neon-blue: #00E5FF;
            --neon-green: #06C755;
            --neon-gold: #FFD700;
            --neon-red: #FF3B30;
            --text-main: #FFFFFF;
            --text-sub: #94A3B8;
            --border: #1E293B;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: 'Noto Sans TC', sans-serif;
            background-image: radial-gradient(circle at 50% 0%, rgba(0, 229, 255, 0.12) 0%, transparent 60%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 24px 16px;
        }
        .container { max-width: 720px; width: 100%; }
        .header {
            text-align: center;
            margin-bottom: 24px;
        }
        .badge {
            display: inline-block;
            background: rgba(0, 229, 255, 0.15);
            color: var(--neon-blue);
            border: 1px solid var(--neon-blue);
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        h1 {
            font-family: 'Teko', 'Noto Sans TC', sans-serif;
            font-size: 38px;
            letter-spacing: 2px;
            text-transform: uppercase;
            background: linear-gradient(90deg, #FFFFFF, var(--neon-blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }
        .subtitle {
            color: var(--text-sub);
            font-size: 14px;
        }
        .line-box {
            background: linear-gradient(135deg, rgba(6, 199, 85, 0.18), rgba(6, 199, 85, 0.05));
            border: 1.5px solid var(--neon-green);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            margin-bottom: 24px;
            box-shadow: 0 8px 24px rgba(6, 199, 85, 0.2);
        }
        .line-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            background-color: var(--neon-green);
            color: #FFFFFF;
            font-size: 18px;
            font-weight: 700;
            text-decoration: none;
            padding: 14px 28px;
            border-radius: 12px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 4px 16px rgba(6, 199, 85, 0.4);
            transition: all 0.2s;
            margin-top: 10px;
        }
        .line-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(6, 199, 85, 0.6);
        }
        .line-id-tip {
            font-size: 13px;
            color: var(--text-sub);
            margin-top: 10px;
        }
        .line-id-tip span {
            color: var(--neon-gold);
            font-weight: 700;
        }
        .sim-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(10px);
            margin-bottom: 24px;
        }
        .sim-title {
            font-size: 16px;
            font-weight: 700;
            color: var(--neon-blue);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .input-group {
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
        }
        input[type="text"] {
            flex: 1;
            background: #1E293B;
            border: 1px solid #334155;
            color: #FFFFFF;
            padding: 12px 16px;
            border-radius: 10px;
            font-size: 15px;
            outline: none;
        }
        input[type="text"]:focus {
            border-color: var(--neon-blue);
        }
        .analyze-btn {
            background: linear-gradient(135deg, #0284C7, #0369A1);
            color: #FFFFFF;
            border: none;
            padding: 0 20px;
            border-radius: 10px;
            font-weight: 700;
            font-size: 15px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .analyze-btn:hover {
            background: linear-gradient(135deg, #0EA5E9, #0284C7);
        }
        .quick-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 16px;
        }
        .tag {
            background: #1E293B;
            color: #CBD5E1;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            border: 1px solid #334155;
        }
        .tag:hover {
            border-color: var(--neon-blue);
            color: var(--neon-blue);
        }
        #result-box {
            display: none;
            margin-top: 16px;
            border-top: 1px solid var(--border);
            padding-top: 16px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 16px;
        }
        .stat-item {
            background: #111827;
            padding: 10px;
            border-radius: 8px;
        }
        .stat-header {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-sub);
            margin-bottom: 6px;
        }
        .bar-bg {
            background: #1F2937;
            height: 6px;
            border-radius: 3px;
            overflow: hidden;
        }
        .bar-fill {
            height: 100%;
            border-radius: 3px;
        }
        .coach-review {
            background: #111827;
            border-left: 4px solid var(--neon-gold);
            padding: 14px;
            border-radius: 8px;
            font-size: 14px;
            line-height: 1.6;
            color: #E2E8F0;
            white-space: pre-wrap;
        }
        .beyblade-preview-img {
            width: 100%;
            max-height: 220px;
            object-fit: contain;
            border-radius: 10px;
            margin-bottom: 14px;
            background: #000000;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            background-color: var(--neon-green);
            border-radius: 50%;
            display: inline-block;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(1.2); }
            100% { opacity: 1; transform: scale(1); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="badge"><span class="status-dot"></span> 24H 雲端整備區 LIVE (SINGAPORE)</div>
            <h1>BEYBLADE X TACTICAL COACH</h1>
            <div class="subtitle">全球頂尖《戰鬥陀螺 X》職業聯賽戰術教練與改裝大師</div>
        </div>

        <div class="line-box">
            <div style="display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 16px;">
                <img src="/avatar.jpg" alt="戰術教練頭像" style="width: 84px; height: 84px; border-radius: 50%; border: 2.5px solid var(--neon-gold); box-shadow: 0 0 20px rgba(255, 215, 0, 0.45); object-fit: cover;">
                <div style="text-align: left;">
                    <div style="font-size: 18px; font-weight: bold; color: #FFFFFF;">《戰鬥陀螺 X》戰術教練</div>
                    <div style="font-size: 13px; color: var(--text-sub);">LINE 專屬 ID：<span style="color: var(--neon-gold); font-weight: bold;">@426cdouo</span></div>
                    <a href="/avatar.jpg" download="beyblade_coach_avatar.jpg" style="display: inline-block; margin-top: 4px; font-size: 12px; color: var(--neon-blue); text-decoration: underline; font-weight: bold;">📥 點此下載這張專屬電競頭像</a>
                </div>
            </div>
            <a href="https://line.me/R/ti/p/@426cdouo" target="_blank" class="line-btn">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="#FFFFFF"><path d="M24 10.304c0-5.369-5.383-9.738-12-9.738-6.616 0-12 4.369-12 9.738 0 4.814 4.269 8.846 10.036 9.608.391.084.922.258 1.057.592.121.303.079.778.039 1.085l-.171 1.027c-.053.303-.242 1.185 1.039.646 1.281-.54 6.911-4.069 9.428-6.967 1.739-1.907 2.572-3.899 2.572-5.991"/></svg>
                開啟 LINE 加入戰術教練
            </a>
            <div style="margin-top: 14px; font-size: 13px; color: #CBD5E1;">
                ⚙️ 更名與換頭像直達：<a href="https://manager.line.biz/account/@426cdouo/setting" target="_blank" style="color: var(--neon-gold); text-decoration: underline; font-weight: bold;">前往 LINE 官方帳號設定中心</a>
            </div>
        </div>

        <div class="sim-card">
            <div class="sim-title">⚡ 線上即時戰術模擬測試台</div>
            <div class="input-group">
                <input type="text" id="comboInput" value="Phoenix Wing 9-60O" placeholder="例如：Phoenix Wing 9-60O 或 魔導權杖 7-60B">
                <button class="analyze-btn" id="analyzeBtn" onclick="runAnalysis()">開始拆解</button>
            </div>
            <div class="quick-tags">
                <span class="tag" onclick="quickFill('Phoenix Wing 9-60O')">鳳凰羽翼 9-60O</span>
                <span class="tag" onclick="quickFill('Wizard Rod 7-60B')">魔導權杖 7-60B</span>
                <span class="tag" onclick="quickFill('Dran Buster 1-60F')">龍之爆裂 1-60F</span>
                <span class="tag" onclick="quickFill('Cobalt Dragoon 2-60C')">蒼白龍騎士 2-60C</span>
                <span class="tag" onclick="quickFill('Shark Edge 3-60LF')">鯊魚之刃 3-60LF</span>
            </div>

            <div id="loading" style="display: none; text-align: center; color: var(--neon-blue); padding: 20px;">
                ⚡ 戰術大腦深度推理中，正在計算物理重心與極速線嚙合...
            </div>

            <div id="result-box">
                <img id="comboImg" class="beyblade-preview-img" src="" alt="陀螺參考圖">
                <h3 id="comboName" style="color: var(--neon-gold); font-size: 20px; margin-bottom: 4px;"></h3>
                <div id="comboSub" style="color: var(--text-sub); font-size: 13px; margin-bottom: 12px;"></div>
                
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-header"><span>一、攻擊破壞力</span><span id="atkVal" style="color: #FF3B30; font-weight: bold;"></span></div>
                        <div class="bar-bg"><div id="atkBar" class="bar-fill" style="background: #FF3B30;"></div></div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-header"><span>二、極致持久力</span><span id="staVal" style="color: #34C759; font-weight: bold;"></span></div>
                        <div class="bar-bg"><div id="staBar" class="bar-fill" style="background: #34C759;"></div></div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-header"><span>三、防禦抗爆力</span><span id="defVal" style="color: #007AFF; font-weight: bold;"></span></div>
                        <div class="bar-bg"><div id="defBar" class="bar-fill" style="background: #007AFF;"></div></div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-header"><span>四、X-Dash 突襲率</span><span id="xdashVal" style="color: #FF9500; font-weight: bold;"></span></div>
                        <div class="bar-bg"><div id="xdashBar" class="bar-fill" style="background: #FF9500;"></div></div>
                    </div>
                </div>

                <div class="coach-review" id="coachText"></div>
            </div>
        </div>
    </div>

    <script>
        function quickFill(val) {
            document.getElementById('comboInput').value = val;
            runAnalysis();
        }

        async function runAnalysis() {
            const input = document.getElementById('comboInput').value.trim();
            if (!input) return;

            const btn = document.getElementById('analyzeBtn');
            const loading = document.getElementById('loading');
            const resultBox = document.getElementById('result-box');

            btn.disabled = true;
            loading.style.display = 'block';
            resultBox.style.display = 'none';

            try {
                const res = await fetch('/api/simulate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: input})
                });
                const data = await res.json();
                
                loading.style.display = 'none';
                btn.disabled = false;
                resultBox.style.display = 'block';

                if (data.combo_stats) {
                    const s = data.combo_stats;
                    document.getElementById('comboName').textContent = s.combo_name;
                    document.getElementById('comboSub').textContent = `${s.combo_name_zh} | 總配重：約 ${s.total_weight_g}g`;
                    document.getElementById('comboImg').src = s.hero_image_url || '';
                    document.getElementById('comboImg').style.display = s.hero_image_url ? 'block' : 'none';

                    document.getElementById('atkVal').textContent = s.scores.attack + '/100';
                    document.getElementById('atkBar').style.width = s.scores.attack + '%';
                    document.getElementById('staVal').textContent = s.scores.stamina + '/100';
                    document.getElementById('staBar').style.width = s.scores.stamina + '%';
                    document.getElementById('defVal').textContent = s.scores.defense + '/100';
                    document.getElementById('defBar').style.width = s.scores.defense + '%';
                    document.getElementById('xdashVal').textContent = s.scores.xdash + '/100';
                    document.getElementById('xdashBar').style.width = s.scores.xdash + '%';
                }

                document.getElementById('coachText').textContent = data.reply_text || '戰術分析完成。';
            } catch (err) {
                loading.style.display = 'none';
                btn.disabled = false;
                alert('連線分析逾時，請再試一次！');
            }
        }
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def index():
    return LANDING_HTML

@app.get("/avatar.jpg")
def get_avatar_image():
    avatar_file = Path(__file__).resolve().parent / "avatar.jpg"
    if avatar_file.exists():
        return FileResponse(avatar_file, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Avatar image not found")

@app.get("/api/status")
def status_info():
    return {
        "status": "online",
        "service": "Beyblade X Professional Tactical Coach LINE Bot",
        "registered_parts": {
            "blades": len(db.blades),
            "ratchets": len(db.ratchets),
            "bits": len(db.bits)
        },
        "webhook_endpoint": "/callback",
        "sim_endpoint": "/api/simulate"
    }

@app.get("/health")
def health():
    return {"status": "ok", "db_ready": len(db.blades) > 0}

@app.post("/callback")
async def line_callback(request: Request, x_line_signature: Optional[str] = Header(None)):
    if not line_webhook_handler:
        raise HTTPException(status_code=500, detail="LINE Webhook Handler is not configured.")
    if not x_line_signature:
        raise HTTPException(status_code=400, detail="Missing X-Line-Signature header.")

    body = await request.body()
    body_str = body.decode("utf-8")

    try:
        line_webhook_handler.handle(body_str, x_line_signature)
    except Exception as e:
        logger.error(f"Webhook handling error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={"status": "handled"})

class SimRequest(BaseModel):
    message: str

@app.post("/api/simulate")
def simulate_coach_analysis(req: SimRequest):
    """
    Endpoint for testing coach output and Flex message payloads directly via HTTP
    """
    result = coach_engine.analyze(req.message)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
