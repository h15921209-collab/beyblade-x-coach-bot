import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Header, BackgroundTasks
from fastapi.responses import JSONResponse
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

@app.get("/")
def index():
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
