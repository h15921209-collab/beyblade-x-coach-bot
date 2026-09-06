import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import requests
from PIL import Image, ImageDraw, ImageFont
from config import settings

WIDTH = 2500
HEIGHT = 1686
ROW_HEIGHT = HEIGHT // 2
COL_WIDTH = WIDTH // 3

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "web" / "static" / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_IMG = OUTPUT_DIR / "rich_menu_2500x1686.png"

def get_font(size: int, bold: bool = True):
    font_names = ["msjhbd.ttc", "msjh.ttc", "arialbd.ttf", "arial.ttf"]
    for fn in font_names:
        p = Path("C:/Windows/Fonts") / fn
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    return ImageFont.load_default()

def create_rich_menu_image() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), color="#0B0F19")
    draw = ImageDraw.Draw(img)

    # Cyber Grid Background lines
    grid_color = "#131C2E"
    for x in range(0, WIDTH, 50):
        draw.line([(x, 0), (x, HEIGHT)], fill=grid_color, width=1)
    for y in range(0, HEIGHT, 50):
        draw.line([(0, y), (WIDTH, y)], fill=grid_color, width=1)

    # 6 Panels Configuration
    # (col, row, icon, title_zh, sub_en, accent_color, border_color)
    buttons = [
        # Row 0
        (0, 0, "🔥", "賽事頂級主流", "S-TIER META COMBOS", "#FFD700", "#FFD700"),
        (1, 0, "⚡", "極限攻擊刺客", "X-DASH ATTACK KILLERS", "#FF3B30", "#FF3B30"),
        (2, 0, "🛡️", "持久防禦要塞", "STAMINA & DEFENSE TANKS", "#00E5FF", "#00E5FF"),
        # Row 1
        (0, 1, "🧩", "核心零件百科", "PARTS SPEC CATALOG", "#A855F7", "#A855F7"),
        (1, 1, "🛠️", "自訂組合健檢", "CUSTOM TUNING & RADAR", "#06C755", "#06C755"),
        (2, 1, "🌐", "24H 雲端整備區", "LIVE WEB SIMULATOR", "#38BDF8", "#38BDF8"),
    ]

    font_icon = get_font(90, bold=True)
    font_title = get_font(68, bold=True)
    font_sub = get_font(34, bold=False)
    font_tag = get_font(26, bold=True)

    pad = 20
    for col, row, icon, title, sub, accent, border in buttons:
        x0 = col * COL_WIDTH + pad
        y0 = row * ROW_HEIGHT + pad
        x1 = (col + 1) * COL_WIDTH - pad
        y1 = (row + 1) * ROW_HEIGHT - pad

        # Card background with subtle gradient
        card_bg = "#111827"
        draw.rounded_rectangle([x0, y0, x1, y1], radius=32, fill=card_bg, outline=border, width=4)

        # Inner neon highlight bar at top of card
        draw.rounded_rectangle([x0 + 16, y0 + 16, x1 - 16, y0 + 26], radius=5, fill=accent)

        # Center content coordinates
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2

        # Draw Icon (Emoji)
        draw.text((cx, cy - 140), icon, font=font_icon, fill=accent, anchor="mm")

        # Draw Chinese Title
        draw.text((cx, cy - 10), title, font=font_title, fill="#FFFFFF", anchor="mm")

        # Draw English Subtitle
        draw.text((cx, cy + 85), sub, font=font_sub, fill="#94A3B8", anchor="mm")

        # Draw Bottom Action Pill
        pill_w, pill_h = 240, 50
        px0, py0 = cx - pill_w // 2, cy + 180
        px1, py1 = cx + pill_w // 2, py0 + pill_h
        draw.rounded_rectangle([px0, py0, px1, py1], radius=25, fill=accent)
        action_label = "開啟測試台 ↗" if "整備區" in title else "一鍵呼叫 ⚡"
        pill_text_color = "#0A0D14"
        draw.text((cx, py0 + pill_h // 2), action_label, font=font_tag, fill=pill_text_color, anchor="mm")

    # Outer decorative frame
    draw.rectangle([0, 0, WIDTH - 1, HEIGHT - 1], outline="#1E293B", width=6)
    
    img.save(OUTPUT_IMG, "PNG", quality=95)
    print(f"Rich Menu image successfully generated at {OUTPUT_IMG}")
    return img

def upload_and_set_rich_menu(image_path: Path):
    token = settings.LINE_CHANNEL_ACCESS_TOKEN
    if not token:
        print("ERROR: Missing LINE_CHANNEL_ACCESS_TOKEN in settings.")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Rich Menu Area Schema (2 rows x 3 cols)
    # Area bounds: x, y, width, height
    areas = []
    actions = [
        {"type": "message", "text": "【賽事頂級主流】"},
        {"type": "message", "text": "【極限攻擊刺客】"},
        {"type": "message", "text": "【持久防禦要塞】"},
        {"type": "message", "text": "【核心零件百科】"},
        {"type": "message", "text": "【自訂組合健檢】"},
        {"type": "uri", "uri": "https://beyblade-x-coach-bot.onrender.com/"}
    ]

    idx = 0
    for row in range(2):
        for col in range(3):
            areas.append({
                "bounds": {
                    "x": col * COL_WIDTH,
                    "y": row * ROW_HEIGHT,
                    "width": COL_WIDTH,
                    "height": ROW_HEIGHT
                },
                "action": actions[idx]
            })
            idx += 1

    menu_payload = {
        "size": {"width": WIDTH, "height": HEIGHT},
        "selected": True,
        "name": "Beyblade_X_Tactical_Rich_Menu_v1",
        "chatBarText": "⚡ 戰術指揮中心",
        "areas": areas
    }

    print("Step 1: Registering Rich Menu structure with LINE API...")
    res = requests.post("https://api.line.me/v2/bot/richmenu", headers=headers, json=menu_payload)
    if res.status_code != 200:
        print(f"Failed to create rich menu: {res.status_code} - {res.text}")
        return
    
    rich_menu_id = res.json().get("richMenuId")
    print(f"  Success! Created richMenuId: {rich_menu_id}")

    print("Step 2: Uploading 2500x1686 image content...")
    upload_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "image/png"
    }
    with open(image_path, "rb") as f:
        img_bytes = f.read()

    upload_url = f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content"
    upload_res = requests.post(upload_url, headers=upload_headers, data=img_bytes)
    if upload_res.status_code != 200:
        print(f"Failed to upload image: {upload_res.status_code} - {upload_res.text}")
        return
    print("  Success! Image uploaded to LINE CDN.")

    print("Step 3: Setting this menu as DEFAULT for ALL users of @426cdouo...")
    set_url = f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}"
    set_res = requests.post(set_url, headers={"Authorization": f"Bearer {token}"})
    if set_res.status_code == 200:
        print(f"[SUCCESS] Rich Menu {rich_menu_id} is now LIVE and ACTIVE for ALL LINE USERS!")
    else:
        print(f"Failed to set default: {set_res.status_code} - {set_res.text}")

if __name__ == "__main__":
    print("=== BEYBLADE X LINE RICH MENU SETUP ===")
    img = create_rich_menu_image()
    upload_and_set_rich_menu(OUTPUT_IMG)
