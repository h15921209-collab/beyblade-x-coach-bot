import os
import sys
import json
import logging
import re
import requests
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sync_threads")
DATA_PATH = os.path.join(BASE_DIR, "data", "community_insights.json")

THREADS_PROFILES = [
    {"username": "beybladehub.app", "author": "BeybladeHub"},
    {"username": "dada_z77", "author": "DaDa (BeybladeHub 站長)"},
]

def fetch_threads_markdown(username: str) -> str:
    """
    Fetches clean markdown of public Threads profile using Jina AI reader.
    """
    url = f"https://r.jina.ai/https://www.threads.net/@{username}"
    logger.info(f"Fetching Threads posts for @{username} via Jina reader...")
    try:
        res = requests.get(url, timeout=25)
        if res.status_code == 200 and len(res.text) > 200:
            logger.info(f"Successfully fetched {len(res.text)} chars for @{username}")
            return res.text
        else:
            logger.warning(f"Failed to fetch @{username}, status code: {res.status_code}")
    except Exception as e:
        logger.error(f"Error fetching @{username}: {e}")
    return ""

def extract_insights_with_gemini(raw_markdown: str, author_info: str, api_key: str) -> List[Dict[str, Any]]:
    """
    Uses Gemini API to extract tactical, mechanical, and tournament insights from scraped Threads markdown.
    """
    if not api_key:
        logger.warning("No GEMINI_API_KEY found, skipping AI extraction.")
        return []

    prompt = f"""你是一位《戰鬥陀螺 X》(Beyblade X) 台灣資深賽事裁判與數據分析專家。
以下是從台灣知名戰鬥陀螺社群帳號（來源：{author_info}）爬取到的 Threads 貼文內容（Markdown 格式）：

=== 開始貼文內容 ===
{raw_markdown[:15000]}
=== 結束貼文內容 ===

請從中提取出具有「實戰調校價值」、「重量與實測細節」、「賽事主流克制」、「新機體/2.0版本改進」、「發射與賽場攻略」的真實玩家經驗與情報。

請遵守以下規則：
1. 嚴格基於貼文的真實發言與數據提取，嚴禁腦補或虛構（例如確切的實秤克數 37.42g、打擊點填實、美版 34.4g 獨眼巨人 vs 35.4g 魔導神杖、抽獎換色名額等）。
2. 部件名稱請使用台灣代理商官方標準譯名（如：蒼龍神劍、魔導神杖、蒼龍爆刃、鳳凰飛翼、鮫鯊鋒鰭）。
3. 輸出格式必須是純 JSON Array，不可有額外的 Markdown 格式（不可包含 ```json ... ```）：
[
  {{
    "id": "英數唯一識別碼，例如 dransword_20_weight_structure",
    "target_parts": ["適用或提及的部件名稱清單，例如 '蒼龍神劍', 'Dran Sword', '3-60F'"],
    "topic": "主題摘要，例如 '蒼龍神劍 2.0 實秤增重與背面簍空填實'",
    "insight": "提煉出的核心實戰心得與規格細節（精準、實用，字數約 60-150 字）",
    "quote": "貼文中的關鍵原話摘錄",
    "author": "{author_info}",
    "source": "Threads",
    "date": "貼文發布日期（若文中能推斷）"
  }}
]
"""
    models = ["gemini-flash-lite-latest", "gemini-3.6-flash", "gemini-flash-latest"]
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048
        }
    }

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        raw_json_str = parts[0]["text"].strip()
                        raw_json_str = re.sub(r"^```json\s*", "", raw_json_str)
                        raw_json_str = re.sub(r"^```\s*", "", raw_json_str)
                        raw_json_str = re.sub(r"\s*```$", "", raw_json_str)
                        parsed = json.loads(raw_json_str)
                        if isinstance(parsed, list):
                            logger.info(f"Successfully extracted {len(parsed)} insights via {model}")
                            return parsed
            else:
                logger.warning(f"Model {model} returned HTTP {res.status_code}: {res.text[:120]}")
        except Exception as e:
            logger.warning(f"Failed extraction with model {model}: {e}")

    return []

def sync_threads():
    from config import settings
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")

    existing_insights = []
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                existing_insights = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read existing insights: {e}")

    insight_map = {item["id"]: item for item in existing_insights if "id" in item}
    total_new = 0

    for prof in THREADS_PROFILES:
        md = fetch_threads_markdown(prof["username"])
        if not md:
            continue
        insights = extract_insights_with_gemini(md, prof["author"], api_key)
        for ins in insights:
            ins_id = ins.get("id")
            if not ins_id:
                continue
            if ins_id not in insight_map:
                total_new += 1
            insight_map[ins_id] = ins

    if not insight_map:
        logger.info("Initializing baseline high-value community insights...")
        baseline = [
            {
                "id": "dransword_20_weight_structure",
                "target_parts": ["蒼龍神劍", "Dran Sword", "3-60F", "BX-00", "神劍"],
                "topic": "蒼龍神劍 2.0 實秤增重與背面簍空填實結構調校",
                "insight": "2.0 版將初代 BX-01 背面三個打擊點原本簍空之處全數填實，上蓋實秤自原本約 34g 大幅激增至 37.42g（已超越蒼龍爆刃 36.5g，與鮫鯊鋒鰭均重相當）。攻擊剛性極大幅提升，開局 X-Dash 衝撞破壞力驚人。",
                "quote": "背面三個打擊點原本簍空的地方 2.0 版全部填實了 上蓋從 34 克出頭 加到 37.42 克 比爆刃36.5 克還重 跟鯊魚平均差不多",
                "author": "BeybladeHub",
                "source": "Threads @beybladehub.app",
                "date": "2026-08-05"
            },
            {
                "id": "glare_cyclops_vs_wizard_rod",
                "target_parts": ["魔導神杖", "Wizard Rod", "獨眼巨人", "Glare Cyclops"],
                "topic": "美版獨眼巨人（Glare Cyclops）挑戰魔導神杖持久霸主地位",
                "insight": "美版獨眼巨人實體秤重上蓋約 34.4g，具備近乎完美正圓形輪廓，僅比賽事持久霸主魔導神杖（35.4g）輕 1g。外圓滾動離心力與受撞滑差極佳，被視為衝擊魔導神杖持久地位的強力挑戰者。",
                "quote": "獨眼巨人 Glare Cyclops 美版那邊已經開始在賣 上蓋重約 34.4g 幾乎全圓的外型 跟魔導神杖的 35.4g 差 1g，這會不會推翻魔導神杖的地位？",
                "author": "BeybladeHub",
                "source": "Threads @beybladehub.app",
                "date": "2026-08-27"
            },
            {
                "id": "phoenix_wing_weight_tuning",
                "target_parts": ["鳳凰飛翼", "Phoenix Wing", "9-60O", "9-60"],
                "topic": "台灣 G1 冠軍選手電子秤極限克重調校心得",
                "insight": "頂尖賽事選手皆配備 0.01g 高精度電子秤挑選出廠公差。鳳凰飛翼實秤若能達到 39.3g 極限公差，搭配 9-60 緊實公差與 Orb/Ball 軸，具備極強的下沉壓制力與防撬爆剛性。",
                "quote": "想要能把小孩打哭的陀螺 預算無上限...克數還標到精準 39.3 克，真正的陀螺玩家都會有一個電子秤",
                "author": "DaDa (BeybladeHub 站長)",
                "source": "Threads @dada_z77",
                "date": "2026-07-21"
            }
        ]
        for item in baseline:
            insight_map[item["id"]] = item
        total_new += len(baseline)

    final_list = list(insight_map.values())
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved {len(final_list)} community insights (new: {total_new}) to {DATA_PATH}")
    return final_list

if __name__ == "__main__":
    sync_threads()
