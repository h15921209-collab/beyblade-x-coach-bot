import re
import math
from typing import Optional, Dict, Any, Tuple
from core.database import db

def parse_matchup_query(text: str) -> Optional[Tuple[str, str]]:
    patterns = [
        r"\s+vs\.?\s+",
        r"\s*VS\s*",
        r"\s*vs\s*",
        r"\s*對決\s*",
        r"\s*打\s*",
        r"\s*PK\s*",
        r"\s*pk\s*",
        r"\s*對抗\s*"
    ]
    for pat in patterns:
        parts = re.split(pat, text, flags=re.IGNORECASE)
        if len(parts) == 2:
            a, b = parts[0].strip(), parts[1].strip()
            a = re.sub(r"^[🎯⚔️🛡️🔥\s]+(?:模擬對戰|對戰|挑戰|對決)?\s*", "", a).strip()
            b = re.sub(r"^[🎯⚔️🛡️🔥\s]+(?:模擬對戰|對戰|挑戰|對決)?\s*", "", b).strip()
            if a and b:
                return (a, b)
    return None

def resolve_combo(text: str) -> Optional[Dict[str, Any]]:
    parsed = db.parse_combo_from_text(text)
    if parsed:
        b, r, bit = parsed
        return db.calculate_combo_stats(b, r, bit)

    blade = db.find_blade(text)
    if blade:
        r = db.find_ratchet("9-60") or db.find_ratchet("5-60") or db.ratchets[0]
        if blade.get("type") == "Attack":
            bit = db.find_bit("F") or db.bits[0]
        elif blade.get("type") == "Stamina":
            bit = db.find_bit("B") or db.bits[0]
        elif blade.get("type") == "Defense":
            bit = db.find_bit("N") or db.bits[0]
        else:
            bit = db.find_bit("T") or db.bits[0]
        return db.calculate_combo_stats(blade, r, bit)

    return None

def simulate_matchup(query_text: str) -> Optional[Dict[str, Any]]:
    pair = parse_matchup_query(query_text)
    if not pair:
        return None

    raw_a, raw_b = pair
    stats_a = resolve_combo(raw_a)
    stats_b = resolve_combo(raw_b)

    if not stats_a or not stats_b:
        return None

    w_a = stats_a.get("total_weight_g", 43.0)
    w_b = stats_b.get("total_weight_g", 43.0)
    type_a = stats_a["blade"].get("type", "Balance")
    type_b = stats_b["blade"].get("type", "Balance")
    atk_a = stats_a["scores"]["attack"]
    atk_b = stats_b["scores"]["attack"]
    sta_a = stats_a["scores"]["stamina"]
    sta_b = stats_b["scores"]["stamina"]
    def_a = stats_a["scores"]["defense"]
    def_b = stats_b["scores"]["defense"]
    dash_a = stats_a["scores"].get("xdash", 50)
    dash_b = stats_b["scores"].get("xdash", 50)

    def get_height(ratchet_dict):
        m = re.search(r"([678]0)", ratchet_dict.get("name", "60"))
        return int(m.group(1)) if m else 60

    h_a = get_height(stats_a["ratchet"])
    h_b = get_height(stats_b["ratchet"])

    score_a = 50.0
    score_b = 50.0

    w_diff = w_a - w_b
    score_a += w_diff * 2.5
    score_b -= w_diff * 2.5

    if h_a < h_b:
        score_a += 6.0
        score_b -= 6.0
    elif h_a > h_b:
        score_a -= 6.0
        score_b += 6.0

    if type_a == "Attack" and type_b == "Stamina":
        score_a += 4.0
        score_b -= 4.0
    elif type_a == "Stamina" and type_b == "Attack":
        score_a -= 4.0
        score_b += 4.0
    elif type_a == "Stamina" and type_b == "Defense":
        score_a += 5.0
        score_b -= 5.0
    elif type_a == "Defense" and type_b == "Stamina":
        score_a -= 5.0
        score_b += 5.0
    elif type_a == "Attack" and type_b == "Defense":
        score_a -= 3.0
        score_b += 3.0
    elif type_a == "Defense" and type_b == "Attack":
        score_a += 3.0
        score_b -= 3.0

    win_rate_a = max(20, min(80, int(round(score_a))))
    win_rate_b = 100 - win_rate_a

    if type_a == "Attack" or type_b == "Attack":
        over_pct = int(min(65, max(30, (dash_a + dash_b) / 3.5)))
        burst_pct = int(min(35, max(15, (atk_a + atk_b) / 7.0 + (abs(h_a - h_b) * 2))))
        spin_pct = max(10, 100 - over_pct - burst_pct)
    else:
        spin_pct = int(min(75, max(45, (sta_a + sta_b) / 2.8)))
        burst_pct = int(min(25, max(10, (atk_a + atk_b) / 10.0)))
        over_pct = max(10, 100 - spin_pct - burst_pct)

    tot = over_pct + burst_pct + spin_pct
    over_pct = int(round(over_pct * 100 / tot))
    burst_pct = int(round(burst_pct * 100 / tot))
    spin_pct = 100 - over_pct - burst_pct

    b_name_b = stats_b["ratchet"]["name"]
    b_zh_a = stats_a["blade"]["name_zh"]
    r_name_a = stats_a["ratchet"]["name"]

    if type_a == "Attack":
        advice_a = f"採 15°~20° Banked Launch (斜射進軌)！起手全力下壓咬合 X-Line 軌道發動極限加速衝撞，直接瞄準對手 {b_name_b} 墊片(軸環)低位挑擊，力求前 25 秒內達成【擊出出場 (Over Finish)】！"
    elif type_a == "Stamina":
        advice_a = f"採標準 Flat Launch (微偏心平射定心)！適度控制拉線力量避免自爆出界，落地後迅速沉降於中央低阻力區，以【{b_zh_a}】的高外圈離心慣性耗盡對手轉速，力求【迴轉終結 (Spin Finish)】！"
    else:
        advice_a = f"採 Parallel Launch (平行軌道切入)！手腕保持平穩鎖死中心，以【{r_name_a}】低重心抵抗對手撞擊，專注防守反擊並尋求【爆裂擊破 (Burst Finish)】機會！"

    if type_b == "Attack":
        advice_b = f"警戒對手第一波 X-Dash 衝刺！發射時需微調落點偏離對手衝線角度，避免開局正面硬碰硬遭擊出出場。"
    else:
        advice_b = f"注意防範對手持久消耗！若無法於前兩次咬軌衝刺重創對方，尾盤轉速將處於迴轉劣勢。"

    return {
        "combo_a": stats_a,
        "combo_b": stats_b,
        "win_rate_a": win_rate_a,
        "win_rate_b": win_rate_b,
        "finish_breakdown": {
            "over": over_pct,
            "burst": burst_pct,
            "spin": spin_pct
        },
        "tactical_advice": {
            "corner_a": advice_a,
            "corner_b": advice_b
        },
        "query": query_text
    }