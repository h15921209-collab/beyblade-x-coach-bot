import requests
import json
from pathlib import Path

IMG_DIR = Path("web/static/images")

with open("data/parts_db.json", "r", encoding="utf-8") as f:
    db = json.load(f)

special_bit_map = {
    "LF": ["BitLowFlat.png", "Bit_LowFlat.png", "BitLowflat.png"],
    "GF": ["BitGearFlat.png", "Bit_GearFlat.png"],
    "GP": ["BitGearPoint.png", "Bit_GearPoint.png"],
    "HN": ["BitHighNeedle.png", "Bit_HighNeedle.png"],
    "FB": ["BitFreeBall.png", "Bit_FreeBall.png"],
    "RA": ["BitRubberAccel.png", "Bit_RubberAccel.png"],
    "DB": ["BitDiscBall.png", "Bit_DiscBall.png"],
    "HT": ["BitHighTaper.png", "Bit_HighTaper.png"]
}

for b in db["bits"]:
    bid = b["id"].upper()
    if bid in special_bit_map:
        for fname in special_bit_map[bid]:
            url = f"https://beyblade.fandom.com/api.php?action=query&titles=File:{fname}&prop=imageinfo&iiprop=url&format=json"
            try:
                res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).json()
                pages = res.get("query", {}).get("pages", {})
                for pid, p in pages.items():
                    if pid != "-1":
                        img_url = p.get("imageinfo", [{}])[0].get("url")
                        if img_url:
                            local_name = f"bit_{bid.lower()}.png"
                            data = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).content
                            with open(IMG_DIR / local_name, "wb") as out:
                                out.write(data)
                            b["image_local"] = f"/static/images/{local_name}"
                            b["image_url"] = img_url
                            print(f"Downloaded bit {bid}: {local_name}")
                            break
            except Exception as e:
                pass
            if b.get("image_local"):
                break

with open("data/parts_db.json", "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("Special bits finished.")
