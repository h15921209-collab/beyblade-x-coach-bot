import json
import re
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from config import settings

class BeybladeDatabase:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.PARTS_DB_PATH
        self.blades: List[Dict[str, Any]] = []
        self.ratchets: List[Dict[str, Any]] = []
        self.bits: List[Dict[str, Any]] = []
        self.load_database()

    def load_database(self):
        if not self.db_path.exists():
            raise FileNotFoundError(f"Parts DB not found at {self.db_path}")
        with open(self.db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.blades = data.get("blades", [])
            self.ratchets = data.get("ratchets", [])
            self.bits = data.get("bits", [])

    def _normalize(self, text: str) -> str:
        return re.sub(r"[\s\-_/()（）]", "", text).lower()

    def find_blade(self, query: str) -> Optional[Dict[str, Any]]:
        clean_q = self._normalize(query)
        # 1. Exact or substring match on id, name, name_zh, code
        for b in self.blades:
            if clean_q == self._normalize(b["id"]) or clean_q == self._normalize(b["name"]) or clean_q == self._normalize(b["name_zh"]) or clean_q == self._normalize(b.get("code", "")):
                return b
        for b in self.blades:
            if clean_q in self._normalize(b["name"]) or clean_q in self._normalize(b["name_zh"]) or clean_q in self._normalize(b["id"]):
                return b
        # Keyword partials (e.g. "phoenix", "鳳凰", "rod", "魔導", "buster", "爆裂")
        for b in self.blades:
            for part in [b["name"].lower().split(), b["name_zh"]]:
                if isinstance(part, list):
                    for p in part:
                        if len(p) >= 3 and p in clean_q:
                            return b
                elif len(part) >= 2 and part in clean_q:
                    return b
        return None

    def find_ratchet(self, query: str) -> Optional[Dict[str, Any]]:
        clean_q = self._normalize(query)
        # Check standard formats like 960 -> 9-60, 560 -> 5-60
        m = re.search(r"(\d)[-_]?(\d{2})", clean_q)
        target_norm = f"{m.group(1)}{m.group(2)}" if m else clean_q

        for r in self.ratchets:
            r_norm = self._normalize(r["name"])
            if target_norm == r_norm or clean_q == r_norm:
                return r
        for r in self.ratchets:
            if clean_q in self._normalize(r["name"]):
                return r
        return None

    def find_bit(self, query: str) -> Optional[Dict[str, Any]]:
        clean_q = self._normalize(query)
        # Direct match on ID (e.g. "f", "t", "b", "o", "p", "lf", "gf", "fb", "ra")
        for bit in self.bits:
            if clean_q == self._normalize(bit["id"]):
                return bit
        # Match name or Chinese description
        for bit in self.bits:
            if clean_q == self._normalize(bit["name"]):
                return bit
            if clean_q in self._normalize(bit["name"]):
                return bit
        return None

    def find_part(self, name: str, category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        cat = category.lower() if category else ""
        if cat in ["blade", "刃"]:
            return self.find_blade(name)
        if cat in ["ratchet", "墊片", "鋼鐵線"]:
            return self.find_ratchet(name)
        if cat in ["bit", "軸", "軸點"]:
            return self.find_bit(name)

        # Auto-detect category
        b = self.find_blade(name)
        if b: return {**b, "_category": "Blade"}
        r = self.find_ratchet(name)
        if r: return {**r, "_category": "Ratchet"}
        bit = self.find_bit(name)
        if bit: return {**bit, "_category": "Bit"}
        return None

    def parse_combo_from_text(self, text: str) -> Optional[Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]]:
        """
        Parses combo like 'Phoenix Wing 9-60O', '魔導權杖 7-60 B', 'Dran Buster 1-60 F'
        """
        # Look for ratchet pattern: 1-60, 3-60, 5-60, 9-60, 7-60, 3-80, 5-70, etc.
        # Matches both separated '9-60 O' and attached '9-60O' or '1-60F'
        ratchet_match = re.search(r"(?:^|[^\d])([1-9])[-_]?([678]0)(?=[a-zA-Z\s\-_.,?!]|$)", text, re.IGNORECASE)
        if not ratchet_match:
            return None

        ratchet_str = f"{ratchet_match.group(1)}-{ratchet_match.group(2)}"
        ratchet = self.find_ratchet(ratchet_str)
        if not ratchet:
            return None

        # Everything before ratchet is likely blade
        blade_part = text[:ratchet_match.start(1)].strip()
        # Everything after ratchet is likely bit
        bit_part = text[ratchet_match.end(2):].strip()

        # If blade is in the prefix
        blade = self.find_blade(blade_part) if blade_part else None
        if not blade:
            # Try searching the entire text for any blade
            for candidate in self.blades:
                if candidate["name"].lower() in text.lower() or candidate["name_zh"] in text:
                    blade = candidate
                    break

        # If bit is in the suffix
        bit = None
        if bit_part:
            # Clean leading punctuation/spaces
            clean_bit_part = re.sub(r"^[\s\-:_]+", "", bit_part).strip()
            # 1. Match known bit IDs at the start of clean_bit_part (sorted by length descending, e.g. GF before F)
            sorted_bits = sorted(self.bits, key=lambda x: len(x["id"]), reverse=True)
            for candidate_bit in sorted_bits:
                bit_id = candidate_bit["id"]
                if re.match(rf"^{bit_id}(?=[^a-zA-Z]|$)", clean_bit_part, re.IGNORECASE):
                    bit = candidate_bit
                    break

            # 2. Try first token split by space or Chinese/English punctuation
            if not bit:
                tokens = re.split(r"[\s\-_，,。？！?!、]+", clean_bit_part)
                first_token = tokens[0] if tokens else ""
                bit = self.find_bit(first_token)
            if not bit:
                bit = self.find_bit(clean_bit_part)

        if not bit:
            sorted_bits = sorted(self.bits, key=lambda x: len(x["id"]), reverse=True)
            for candidate_bit in sorted_bits:
                # Match standalone bit abbreviation
                pattern = rf"(?:^|[\s\-_，,。？！?!、]){candidate_bit['id']}(?:$|[\s\-_，,。？！?!、])"
                if re.search(pattern, text, re.IGNORECASE):
                    bit = candidate_bit
                    break

        if blade and ratchet and bit:
            return (blade, ratchet, bit)
        return None

    def calculate_combo_stats(self, blade: Dict[str, Any], ratchet: Dict[str, Any], bit: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates physical metrics and 4-dimension performance scores (0-100)
        """
        b_weight = float(blade.get("weight_g", 35.0))
        r_weight = float(ratchet.get("weight_g", 6.5))
        bit_weight = float(bit.get("weight_g", 2.2))
        total_weight = round(b_weight + r_weight + bit_weight, 2)

        # 1. Attack Score
        base_attack = 50
        if blade.get("type") == "Attack":
            base_attack += 25
        elif blade.get("type") == "Balance":
            base_attack += 12
        if bit.get("type") == "Attack":
            base_attack += 20
        elif bit.get("type") == "Balance":
            base_attack += 10
        # Weight bonus to attack impact
        weight_bonus = max(0, (total_weight - 43.0) * 3)
        attack_score = min(99, int(base_attack + weight_bonus))

        # 2. Stamina Score
        base_stamina = 45
        if blade.get("type") == "Stamina":
            base_stamina += 30
        elif blade.get("type") == "Balance":
            base_stamina += 15
        if bit.get("type") == "Stamina":
            base_stamina += 22
        elif bit.get("type") == "Defense":
            base_stamina += 10
        # Perimeter inertia bonus
        if "Perimeter" in blade.get("cg", "") or "Outer" in blade.get("cg", ""):
            base_stamina += 6
        stamina_score = min(99, int(base_stamina))

        # 3. Defense Score (Burst & Knockout Resistance)
        base_defense = 40
        if blade.get("type") == "Defense":
            base_defense += 25
        elif blade.get("type") == "Balance":
            base_defense += 12
        if ratchet.get("blades_count", 3) >= 7:
            base_defense += 15
        elif ratchet.get("blades_count", 3) == 5:
            base_defense += 12
        if bit.get("type") == "Defense":
            base_defense += 18
        if "High" in ratchet.get("burst_resistance", ""):
            base_defense += 6
        defense_score = min(99, int(base_defense))

        # 4. X-Dash Capability Score
        base_xdash = 35
        teeth = bit.get("gear_teeth", 16)
        if teeth >= 24:
            base_xdash += 25
        if bit.get("type") == "Attack":
            base_xdash += 28
        elif bit.get("type") == "Balance":
            base_xdash += 15
        if "Extreme" in blade.get("x_dash_capability", ""):
            base_xdash += 12
        xdash_score = min(99, int(base_xdash))

        combo_name = f"{blade['name']} {ratchet['name']}{bit['id']}"
        combo_name_zh = f"{blade['name_zh']} {ratchet['name']}{bit['name']}"

        return {
            "combo_name": combo_name,
            "combo_name_zh": combo_name_zh,
            "total_weight_g": total_weight,
            "blade": blade,
            "ratchet": ratchet,
            "bit": bit,
            "scores": {
                "attack": attack_score,
                "stamina": stamina_score,
                "defense": defense_score,
                "xdash": xdash_score
            },
            "hero_image_url": blade.get("card_image_url") or blade.get("image_url")
        }

db = BeybladeDatabase()
