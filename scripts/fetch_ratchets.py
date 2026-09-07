import requests
import json
from pathlib import Path

IMG_DIR = Path("web/static/images")
IMG_DIR.mkdir(parents=True, exist_ok=True)

with open("data/parts_db.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for r in db["ratchets"]:
    name = r["name"]
    fname = f"Ratchet{name}.png"
    url = f"https://beyblade.fandom.com/api.php?action=query&titles=File:{fname}&prop=imageinfo&iiprop=url&format=json"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).json()
        pages = res.get("query", {}).get("pages", {})
        for pid, p in pages.items():
            if pid != "-1":
                img_url = p.get("imageinfo", [{}])[0].get("url")
                if img_url:
                    local_name = f"ratchet_{name}.png"
                    data = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).content
                    with open(IMG_DIR / local_name, "wb") as out:
                        out.write(data)
                    r["image_local"] = f"/static/images/{local_name}"
                    r["image_url"] = img_url
                    print("Downloaded ratchet:", local_name)
    except Exception as e:
        print(f"Error on {name}: {e}")

with open("data/parts_db.json", "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("Finished fetching ratchets.")
