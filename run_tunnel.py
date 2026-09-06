import re
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOCAL_CLOUDFLARED = BASE_DIR / "cloudflared.exe"
SIBLING_CLOUDFLARED = BASE_DIR.parent / "beyblade-stock-notifier" / "cloudflared.exe"

def find_cloudflared() -> str:
    if LOCAL_CLOUDFLARED.exists():
        return str(LOCAL_CLOUDFLARED)
    if SIBLING_CLOUDFLARED.exists():
        return str(SIBLING_CLOUDFLARED)
    # Check PATH
    return "cloudflared"

def main():
    binary = find_cloudflared()
    print(f"[*] Using cloudflared binary: {binary}")
    print("[*] Starting tunnel for http://localhost:8000 ...")

    cmd = [binary, "tunnel", "--url", "http://localhost:8000"]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    url_found = None
    try:
        for line in iter(process.stdout.readline, ""):
            print(line, end="")
            match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if match and not url_found:
                url_found = match.group(0)
                webhook_url = f"{url_found}/callback"
                print("\n" + "=" * 65)
                print(f"🚀 LINE Webhook 穿透 URL 已就緒：")
                print(f"👉 Webhook URL: {webhook_url}")
                print(f"👉 狀態監控儀表板: {url_found}")
                print("請複製上方 Webhook URL 並貼入 LINE Developers Console 設定！")
                print("=" * 65 + "\n")
                with open(BASE_DIR / "live_url.txt", "w", encoding="utf-8") as f:
                    f.write(webhook_url)
    except KeyboardInterrupt:
        print("\n[*] Stopping tunnel...")
        process.terminate()

if __name__ == "__main__":
    main()
