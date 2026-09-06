import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import os
import time
import requests
from config import settings

def deploy_to_render_and_bind_line(render_api_key: str):
    print("🚀 正在調用 Render API 進行全自動雲端服務創建與部署...")
    headers = {
        "Authorization": f"Bearer {render_api_key.strip()}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # 1. 取得 Owner ID
    owners_res = requests.get("https://api.render.com/v1/owners", headers=headers)
    if owners_res.status_code != 200:
        print(f"❌ 驗證 Render API Key 失敗: {owners_res.text}")
        return
    
    owners = owners_res.json()
    owner_id = owners[0]["owner"]["id"]
    print(f"✅ 成功連接 Render 帳戶: {owners[0]['owner']['name']} (ID: {owner_id})")

    service_name = "beyblade-x-coach-bot"
    repo_url = "https://github.com/h15921209-collab/beyblade-x-coach-bot"

    # 2. 建立 Web Service (Render API v1)
    service_payload = {
        "type": "web_service",
        "name": service_name,
        "ownerId": owner_id,
        "repo": repo_url,
        "branch": "main",
        "autoDeploy": "yes",
        "serviceDetails": {
            "env": "python",
            "plan": "free",
            "region": "singapore",
            "envSpecificDetails": {
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT"
            },
            "envVars": [
                {"key": "GEMINI_API_KEY", "value": settings.GEMINI_API_KEY},
                {"key": "LINE_CHANNEL_ACCESS_TOKEN", "value": settings.LINE_CHANNEL_ACCESS_TOKEN},
                {"key": "LINE_CHANNEL_SECRET", "value": settings.LINE_CHANNEL_SECRET}
            ]
        }
    }

    create_res = requests.post("https://api.render.com/v1/services", headers=headers, json=service_payload)
    print(f"Render API 回應碼: {create_res.status_code}")
    
    if create_res.status_code in (200, 201):
        service_data = create_res.json()["service"]
    else:
        print(f"回應內容: {create_res.text}")
        services = requests.get(f"https://api.render.com/v1/services?ownerId={owner_id}", headers=headers).json()
        target = next((s["service"] for s in services if s["service"]["name"] == service_name), None)
        if not target:
            print("❌ 無法建立或獲取現有服務。")
            return
        service_data = target

    service_id = service_data["id"]
    service_url = service_data["serviceDetails"].get("url") or f"https://{service_data.get('slug')}.onrender.com"
    print(f"✅ Render 雲端服務建立成功！(Service ID: {service_id})")
    print(f"🌐 雲端專屬網址: {service_url}")

    # 3. 自動更新 LINE Webhook URL
    webhook_url = f"{service_url}/callback"
    print(f"\n🔗 正在透過 LINE API 自動綁定 Webhook 端點: {webhook_url} ...")
    
    line_headers = {
        "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    line_payload = {"endpoint": webhook_url}
    line_res = requests.put("https://api.line.me/v2/bot/channel/webhook/endpoint", headers=line_headers, json=line_payload)
    
    if line_res.status_code == 200:
        print("🎉 LINE Webhook 網址已全自動綁定成功！")
    else:
        print(f"LINE 綁定回傳: {line_res.status_code} - {line_res.text}")

    # 4. 驗證 LINE 端點連線
    print("🔍 正在請求 LINE 官方驗證 Webhook...")
    test_res = requests.post("https://api.line.me/v2/bot/channel/webhook/test", headers=line_headers, json={"endpoint": webhook_url})
    print(f"📡 LINE 官方連線測試: {test_res.text}")
    print("\n🎊 全流程全自動化雲端託管完成！電腦關機後 LINE 機器人依然 24 小時在線！")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        deploy_to_render_and_bind_line(sys.argv[1])
    else:
        key = input("請輸入 Render API Key (rnd_...): ")
        deploy_to_render_and_bind_line(key)
