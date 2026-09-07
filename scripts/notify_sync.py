import os
import sys
import requests

def send_notification():
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.environ.get("ADMIN_LINE_USER_ID")
    
    if not token or not user_id:
        print("[NOTIFY] Skipped: LINE_CHANNEL_ACCESS_TOKEN or ADMIN_LINE_USER_ID not configured.")
        return

    msg = (
        "【戰鬥陀螺 X 每日情報巡檢】\n"
        "今日巡檢偵測到最新陀螺部件或 Threads 實戰情報已自動入庫並完成雲端同步！\n"
        "AI 戰術教練與對戰模擬系統已即時更新上線。"
    )

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": msg}]
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            print("[NOTIFY] Successfully pushed LINE notification to admin.")
        else:
            print(f"[NOTIFY] Failed to push notification: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[NOTIFY] Error pushing notification: {e}")

if __name__ == "__main__":
    send_notification()
