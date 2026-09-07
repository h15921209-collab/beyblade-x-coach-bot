import os
import requests
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "parts_db.json"
IMG_DIR = BASE_DIR / "web" / "static" / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

with open(DB_PATH, "r", encoding="utf-8") as f:
    db_data = json.load(f)

# Ensure 2-60 and other key ratchets exist
existing_ratchet_names = {r["name"] for r in db_data["ratchets"]}

new_ratchets = [
    {
        "id": "2-60",
        "name": "2-60",
        "height_mm": 6.0,
        "blades_count": 2,
        "weight_g": 6.4,
        "cg": "Dual Thick Lower Wing (雙厚翼超低重心)",
        "burst_resistance": "High (厚實雙凸塊，抗衝擊性極強)",
        "tier": "S",
        "description": "BX-34 蒼白龍騎士標配專用雙翼墊片。採用厚實的雙突起設計，大幅降低受擊破綻，重心低且平衡支撐性絕佳。",
        "tactical_effect": "提供左迴旋時絕佳的同轉支撐與防擦地穩定性，有效抵抗逆向撞擊帶來的爆裂力道。"
    },
    {
        "id": "4-70",
        "name": "4-70",
        "height_mm": 7.0,
        "blades_count": 4,
        "weight_g": 6.6,
        "cg": "Mid-Height Square (四角中位平衡重心)",
        "burst_resistance": "Medium-High",
        "tier": "A",
        "description": "70 中等高度四刃墊片。提供比 60 墊片更高的離地間隙，避免底部擦地，適合中高度傾斜戰術。",
        "tactical_effect": "增加傾斜旋轉時的迴旋空間，減少與地面的摩擦損耗。"
    },
    {
        "id": "4-80",
        "name": "4-80",
        "height_mm": 8.0,
        "blades_count": 4,
        "weight_g": 6.9,
        "cg": "High Square (高位四角重心)",
        "burst_resistance": "Medium",
        "tier": "B+",
        "description": "80 高位墊片，能從高角度對敵方施加向下壓制打擊，但需注意防範被下擊挑飛。",
        "tactical_effect": "適合高位重壓戰術，剋制低位扁平陀螺。"
    },
    {
        "id": "1-80",
        "name": "1-80",
        "height_mm": 8.0,
        "blades_count": 1,
        "weight_g": 7.1,
        "cg": "Single Extreme Off-Center (單點極度偏心)",
        "burst_resistance": "Medium",
        "tier": "A",
        "description": "單刃偏心高位墊片。配合偏心攻擊刃（如 Dran Buster）可產生劇烈的偏心跳躍式打擊動量。",
        "tactical_effect": "極大化爆發衝擊力，造成對手劇烈震盪。"
    },
    {
        "id": "5-80",
        "name": "5-80",
        "height_mm": 8.0,
        "blades_count": 5,
        "weight_g": 7.0,
        "cg": "High Pentagonal (高位五角均勻重心)",
        "burst_resistance": "Medium-High",
        "tier": "A",
        "description": "高位五角均勻分配墊片，兼具高高度與五刃的多重防護。",
        "tactical_effect": "提供穩定的高位旋轉支撐。"
    }
]

for nr in new_ratchets:
    if nr["name"] not in existing_ratchet_names:
        db_data["ratchets"].append(nr)
        print(f"Added ratchet: {nr['name']}")

# Ensure key bits exist: C (Cyclone), A (Accel), R (Rush), N (Needle), DB (Disc Ball), HT (High Taper), D (Dot)
existing_bit_ids = {b["id"].upper() for b in db_data["bits"]}

new_bits = [
    {
        "id": "C",
        "name": "Cyclone (旋風軸)",
        "type": "Attack",
        "weight_g": 2.3,
        "burst_resistance": "High (高阻尼鎖扣)",
        "gear_teeth": 16,
        "x_dash_capability": "Extreme Vortex Dash (高速氣流衝刺)",
        "tier": "S",
        "description": "BX-34 蒼白龍騎士專用標配軸心。軸心外圍設有螺旋擾流翼，能借助旋轉氣流增加下壓力，兼具暴走入軌與中心戰術回旋能力。",
        "tactical_effect": "專為左迴旋攻擊型量身打造，能完美發揮逆向切入與持續極速衝刺效果。"
    },
    {
        "id": "A",
        "name": "Accel (加速軸)",
        "type": "Attack",
        "weight_g": 2.2,
        "burst_resistance": "Extreme (16齒厚平軸端)",
        "gear_teeth": 16,
        "x_dash_capability": "Very High Acceleration (瞬態急速衝刺)",
        "tier": "S",
        "description": "UX-01 Dran Buster 標配軸心。採用直徑較小但抓地力更強的平底設計，啟動反應極快，入軌瞬間加速度達到巔峰。",
        "tactical_effect": "專門用於第一擊必殺與瞬間 Over Finish，爆發力無人能出其右。"
    },
    {
        "id": "R",
        "name": "Rush (衝刺軸)",
        "type": "Attack",
        "weight_g": 2.2,
        "burst_resistance": "High (16齒細平軸端)",
        "gear_teeth": 16,
        "x_dash_capability": "Multiple Continuous Dashes (多段連續衝刺)",
        "tier": "S",
        "description": "採用細平切削端面的攻擊軸，摩擦阻力小於 F，能達成多次反覆觸碰極速線（X-Line）的連環衝刺。",
        "tactical_effect": "避免一次衝刺後耗盡體力，適合中程纏鬥與多次突襲擊飛戰術。"
    },
    {
        "id": "N",
        "name": "Needle (針軸)",
        "type": "Defense",
        "weight_g": 2.0,
        "burst_resistance": "Low-Medium (標準防禦軸阻尼)",
        "gear_teeth": 16,
        "x_dash_capability": "Stationary Low (定點防守，不易入軌)",
        "tier": "A",
        "description": "尖錐狀針型軸心。將接觸面積縮減至極致單點，牢牢釘在競技場中央，承受外圍攻擊型撞擊時不易移位。",
        "tactical_effect": "防守型陀螺的經典定點軸，利用微小摩擦力保持中心防守反擊。"
    },
    {
        "id": "DB",
        "name": "Disc Ball (碟狀球軸)",
        "type": "Stamina",
        "weight_g": 2.4,
        "burst_resistance": "High (UX 系列防禦鎖扣)",
        "gear_teeth": 16,
        "x_dash_capability": "Stable Smooth Glide (超平穩滑行)",
        "tier": "S",
        "description": "UX-03 Wizard Rod 標配持久軸。在球型軸端上方加裝外圍自由碟盤，大幅提升傾斜時的末端復原力，尾速幾近無損耗。",
        "tactical_effect": "極限持久戰霸主，大幅延長旋轉時間並防止末段側翻擦地。"
    },
    {
        "id": "HT",
        "name": "High Taper (高錐軸)",
        "type": "Balance",
        "weight_g": 2.3,
        "burst_resistance": "Medium-High",
        "gear_teeth": 16,
        "x_dash_capability": "Moderate-Controlled (控球中速入軌)",
        "tier": "A+",
        "description": "加高版本的錐形平衡軸，兼具中心定點與外圍機動性，重心高有利於向下壓制。",
        "tactical_effect": "攻守兼備，提供寬廣的發射傾角容錯率。"
    }
]

for nb in new_bits:
    if nb["id"].upper() not in existing_bit_ids:
        db_data["bits"].append(nb)
        print(f"Added bit: {nb['id']} ({nb['name']})")

# Download Ratchet & Bit images from Fandom
for r in db_data["ratchets"]:
    name_clean = r["name"].replace("-", "")
    fname = f"Ratchet{name_clean}.png"
    url = f"https://beyblade.fandom.com/api.php?action=query&titles=File:{fname}&prop=imageinfo&iiprop=url&format=json"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        pages = res.json().get("query", {}).get("pages", {})
        for pid, p in pages.items():
            if pid != "-1":
                img_url = p.get("imageinfo", [{}])[0].get("url")
                if img_url:
                    local_name = f"ratchet_{r['name']}.png"
                    local_path = IMG_DIR / local_name
                    img_data = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).content
                    with open(local_path, "wb") as out:
                        out.write(img_data)
                    r["image_local"] = f"/static/images/{local_name}"
                    r["image_url"] = img_url
                    print(f"Downloaded ratchet: {local_name}")
    except Exception as e:
        print(f"Ratchet {r['name']} error: {e}")

for b in db_data["bits"]:
    # e.g. BitBall.png, BitFlat.png, BitTaper.png, BitPoint.png, BitLowFlat.png, BitGearFlat.png, BitCyclone.png, BitAccel.png, BitRush.png, BitNeedle.png, BitDiscBall.png
    base_name = b["name"].split()[0] # e.g. "Ball", "Cyclone", "Accel"
    fname = f"Bit{base_name}.png"
    url = f"https://beyblade.fandom.com/api.php?action=query&titles=File:{fname}&prop=imageinfo&iiprop=url&format=json"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        pages = res.json().get("query", {}).get("pages", {})
        for pid, p in pages.items():
            if pid != "-1":
                img_url = p.get("imageinfo", [{}])[0].get("url")
                if img_url:
                    local_name = f"bit_{b['id'].lower()}.png"
                    local_path = IMG_DIR / local_name
                    img_data = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).content
                    with open(local_path, "wb") as out:
                        out.write(img_data)
                    b["image_local"] = f"/static/images/{local_name}"
                    b["image_url"] = img_url
                    print(f"Downloaded bit: {local_name}")
    except Exception as e:
        print(f"Bit {b['id']} error: {e}")

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db_data, f, ensure_ascii=False, indent=2)

print("Ratchets and bits updated successfully!")
