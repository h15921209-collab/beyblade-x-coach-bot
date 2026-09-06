import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import requests
from config import settings

def bind_line_webhook(service_url: str):
    """
    Directly updates the LINE Developers Console Webhook URL via LINE Messaging API.
    """
    clean_url = service_url.strip().rstrip("/")
    if not clean_url.endswith("/callback"):
        webhook_url = f"{clean_url}/callback"
    else:
        webhook_url = clean_url

    print(f"🔗 正在透過 LINE API 自動綁定 Webhook 端點至：{webhook_url} ...")

    headers = {
        "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # 1. Update endpoint
    res = requests.put(
        "https://api.line.me/v2/bot/channel/webhook/endpoint",
        headers=headers,
        json={"endpoint": webhook_url}
    )

    if res.status_code == 200:
        print("✅ LINE 官方 Webhook 網址已綁定成功！")
    else:
        print(f"❌ 綁定失敗: {res.status_code} - {res.text}")
        return

    # 2. Test endpoint
    print("🔍 正在進行 LINE 官方伺服器連線測試...")
    test_res = requests.post(
        "https://api.line.me/v2/bot/channel/webhook/test",
        headers=headers,
        json={"endpoint": webhook_url}
    )
    print(f"📡 LINE 測試結果: {test_res.json()}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        bind_line_webhook(sys.argv[1])
    else:
        url = input("請輸入雲端服務網址 (例如 https://beyblade-coach.onrender.com): ")
        bind_line_webhook(url)
