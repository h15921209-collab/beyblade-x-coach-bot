import os
import re
import requests
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "parts_db.json"
IMG_DIR = BASE_DIR / "web" / "static" / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

with open(DB_PATH, "r", encoding="utf-8") as f:
    db_data = json.load(f)

blades = db_data.get("blades", [])

print(f"Total blades: {len(blades)}")

for b in blades:
    name_no_space = b["name"].replace(" ", "")
    candidates = [
        f"File:Blade{name_no_space}.png",
        f"File:Blade_{name_no_space}.png",
        f"File:{name_no_space}.png",
        f"File:Blade - {b['name']}.png",
        f"File:{b['name'].replace(' ', '_')}.png"
    ]
    query_str = "|".join(candidates)
    url = f"https://beyblade.fandom.com/api.php?action=query&titles={query_str}&prop=imageinfo&iiprop=url&format=json"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    pages = r.json().get("query", {}).get("pages", {})
    found_url = None
    found_title = None
    for pid, p in pages.items():
        if pid != "-1":
            info = p.get("imageinfo", [{}])[0]
            if info.get("url"):
                found_url = info["url"]
                found_title = p["title"]
                break
    
    if not found_url:
        # Search allimages for blade name
        search_url = f"https://beyblade.fandom.com/api.php?action=query&list=allimages&aifrom={name_no_space}&ailimit=10&format=json"
        sr = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        aimgs = sr.json().get("query", {}).get("allimages", [])
        for aim in aimgs:
            if name_no_space.lower() in aim["name"].lower() and ("blade" in aim["name"].lower() or "infobox" in aim["name"].lower() or aim["name"].lower().startswith(name_no_space.lower())):
                found_url = aim.get("url")
                found_title = aim.get("title")
                break
    
    if found_url:
        print(f"FOUND {b['id']}: {found_title} -> {found_url}")
        # Download image
        local_filename = f"blade_{b['id']}.png"
        local_filepath = IMG_DIR / local_filename
        try:
            img_res = requests.get(found_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if img_res.status_code == 200:
                with open(local_filepath, "wb") as img_out:
                    img_out.write(img_res.content)
                print(f"  Downloaded to {local_filename} ({len(img_res.content)} bytes)")
                b["image_local"] = f"/static/images/{local_filename}"
                b["card_image_url"] = found_url
                b["image_url"] = found_url
        except Exception as e:
            print(f"  Error downloading: {e}")
    else:
        print(f"NOT FOUND: {b['id']} ({b['name']})")

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db_data, f, ensure_ascii=False, indent=2)

print("Finished updating database with blade images.")
