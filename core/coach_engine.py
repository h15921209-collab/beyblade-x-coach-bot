import os
import json
import logging
import requests
from typing import Dict, Any, Optional, Tuple, List
from config import settings
from core.database import db
from core.flex_builder import FlexMessageBuilder

logger = logging.getLogger("coach_engine")

COACH_SYSTEM_PROMPT = """你現在是全球頂尖的《戰鬥陀螺 X》(Beyblade X) 職業聯賽戰術教練與改裝大師。
你對目前 BEYBLADE X 的所有部件（包括最新 BX 與 UX 系列的刃、墊片、軸心）的重量、材質、物理重心、以及在極速競技場（Xtreme Stadium）中的極速線（X-Line）軌道表現都瞭如指掌。

請嚴格遵守以下規則與選手交流：
1. 【角色設定】：你講話風格精準、專業、充滿戰術思維。請把使用者當成準備參加世界大賽的職業選手，稱呼對方為「選手」。口吻沉穩霸氣，分析拳拳到肉。
2. 【分析框架】：當選手提供一個搭配，或要求推薦搭配時，你必須從以下四個維度進行深度拆解：
   - 一、攻擊力與極速突襲（X-Dash）的觸發率：分析軸心齒輪與極速線嚙合、入軌角度、首波衝刺威力與 Over Finish 幾率。
   - 二、持久力（旋轉時間）與尾速表現：分析外圍離心力、空氣阻力、末段傾斜摩擦與 Spin Finish 表現。
   - 三、防禦力（抗擊飛、抗爆裂能力）：分析墊片高度（如 60 vs 70 vs 80）、受力接觸角、卡榫阻力與防止被撬爆能力。
   - 四、對戰當前主流熱門搭配的勝率與克制關係：精確評析面對賽事霸主（鳳凰飛翼 Phoenix Wing 9-60O、魔導神杖 Wizard Rod 9-60B/7-60B、蒼龍爆刃 Dran Buster 1-60F、蒼穹龍騎士 Cobalt Dragoon 2-60C）的克制鏈與實戰勝率。
3. 【改裝建議與微調細節】：不要只說「這個很好」，要精確指出改動某個部件（例如將 9-60 改為 5-60，或將大平軸 F 改為錐形軸 T）後，對陀螺的重心高度、傾斜角（Tilt Angle）、衝刺加速度與離心穩定度會帶來什麼具體物理改變。
4. 【發射戰術指引】：在分析最後，提供職業選手專屬的發射手勢與角度指引（如：Flat Launch 平射壓制、Banked Launch 斜射走位、入軌點選擇）。
5. 【台灣代理官方標準名稱】：在提及陀螺時，請嚴格採用台灣代理商（麗嬰國際）官方正式名稱搭配原廠英文代碼（如：鳳凰飛翼 Phoenix Wing、蒼龍爆刃 Dran Buster、魔導神杖 Wizard Rod、蒼穹龍騎士 Cobalt Dragoon、鮫鯊鋒鰭 Shark Edge、暴龍霸擊 Tyranno Beat、惡魔鎖鏈 Hells Chain、蒼龍利刃 Dran Dagger、獨角刺心 Unicorn Sting、霜輝銀狼 Silver Wolf、蒼龍神劍 Dran Sword、惡魔紅鐮 Hells Scythe、騎士重盾 Knight Shield、雄獅巔峰 Leon Crest），切勿使用非官方俗稱或大陸翻譯。
6. 【台灣社群與選手實戰情報】：當提供【台灣社群選手實戰情報（Threads）】時，請在分析或改裝建議中自然融入引用（例如引用 BeybladeHub 實秤數據：蒼龍神劍 2.0 版背面簍空填實增重至 37.42g、魔導神杖面對美版獨眼巨人 34.4g 的持久挑戰、台灣賽事選手用電子秤精準挑選 39.3g 公差等），展現與第一線頂尖賽事實戰同步的專業權威度。
"""

class BeybladeCoachEngine:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.models = ["gemini-flash-lite-latest", "gemini-3.6-flash", "gemini-flash-latest"]

    def _call_gemini_api(self, prompt: str, system_prompt: str = COACH_SYSTEM_PROMPT) -> str:
        """
        Calls Gemini API with failover across available models.
        """
        if not self.api_key:
            return "【戰術終端離線】尚未偵測到有效的 GEMINI_API_KEY，請在 .env 中填入金鑰。"

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 1800
            }
        }

        for model_name in self.models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
            try:
                res = requests.post(url, headers=headers, json=payload, timeout=25)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"].strip()
                else:
                    logger.warning(f"Model {model_name} returned status {res.status_code}: {res.text[:100]}")
            except Exception as e:
                logger.warning(f"Failed to query {model_name}: {e}")

        # Local fallback tactical analysis if offline or rate limited
        return self._generate_offline_tactical_report(prompt)

    def _generate_offline_tactical_report(self, user_msg: str) -> str:
        """
        Deterministic high-accuracy fallback report when API is unavailable.
        """
        parsed = db.parse_combo_from_text(user_msg)
        if parsed:
            b, r, bit = parsed
            stats = db.calculate_combo_stats(b, r, bit)
            return (
                f"選手，戰術分析儀已啟動。針對你的搭配【{stats['combo_name']}】（總重 {stats['total_weight_g']}g）：\n\n"
                f"【一、攻擊力與 X-Dash 觸發率】評分 {stats['scores']['attack']}/100\n"
                f"- 刃部：{b['name_zh']} 重 {b['weight_g']}g，重心屬性：{b['cg']}。\n"
                f"- 軸心 {bit['name']} 具備 {bit['gear_teeth']} 齒輪，X-Line 咬合表現為 {bit['x_dash_capability']}。\n\n"
                f"【二、持久力與尾速表現】評分 {stats['scores']['stamina']}/100\n"
                f"- 空轉阻力與迴旋慣性指標：{stats['scores']['stamina']}/100。\n\n"
                f"【三、防禦力與抗爆裂能力】評分 {stats['scores']['defense']}/100\n"
                f"- 墊片 {r['name']}（高度 {r['height_mm']}mm，{r['blades_count']} 齒刃），抗爆性：{r['burst_resistance']}。\n\n"
                f"【四、主流賽事克制關係】\n"
                f"- 對戰 鳳凰飛翼 Phoenix Wing 9-60O：留意對手 39g 重錘撞擊，避免正面剛硬互衝。\n"
                f"- 對戰 魔導神杖 Wizard Rod 9-60B：若無法在開局兩波 X-Dash 破壞其平衡，尾速將被拉入劣勢泥沼。"
            )
        return "選手，整備區隨時為你待命。請提供你目前想測試的「刃 (Blade)」、「墊片 (Ratchet)」與「軸點 (Bit)」組合，或指定攻擊/防禦/持久特化戰術！"

    def _load_community_insights(self) -> List[Dict[str, Any]]:
        insights_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "community_insights.json")
        if os.path.exists(insights_path):
            try:
                with open(insights_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load community insights: {e}")
        return []

    def find_relevant_insights(self, query_text: str, parts: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        insights = self._load_community_insights()
        if not insights:
            return []

        matched = []
        search_terms = [query_text.lower()]
        if parts:
            for p in parts:
                if isinstance(p, dict):
                    if p.get("name"):
                        search_terms.append(p["name"].lower())
                    if p.get("name_zh"):
                        search_terms.append(p["name_zh"].lower())

        for item in insights:
            target_parts = [t.lower() for t in item.get("target_parts", [])]
            topic = item.get("topic", "").lower()
            insight_text = item.get("insight", "").lower()

            hit = False
            for term in search_terms:
                if any(term in tp or tp in term for tp in target_parts):
                    hit = True
                    break
                if len(term) >= 2 and (term in topic or term in insight_text):
                    hit = True
                    break
            if hit and item not in matched:
                matched.append(item)

        return matched[:3]

    def _format_insights_context(self, insights: List[Dict[str, Any]]) -> str:
        if not insights:
            return ""
        ctx = "\n【台灣社群選手實戰情報（Threads 社群實測與賽事實證）】：\n"
        for ins in insights:
            ctx += f"- 主題：{ins.get('topic')}\n"
            ctx += f"  實戰觀察：{ins.get('insight')}\n"
            if ins.get("quote"):
                ctx += f"  選手原話：「{ins.get('quote')}」（來源：{ins.get('source')} {ins.get('author')}）\n"
        return ctx

    def analyze(self, user_text: str) -> Dict[str, Any]:
        """
        Analyzes user input, queries database, invokes Gemini, and builds appropriate Flex card.
        Returns:
            {
                "reply_text": str,
                "flex_message": Optional[dict],
                "combo_stats": Optional[dict],
                "part_info": Optional[dict]
            }
        """
        # Step 1: Detect if user is submitting or asking about a full combo
        parsed_combo = db.parse_combo_from_text(user_text)
        
        if parsed_combo:
            blade, ratchet, bit = parsed_combo
            combo_stats = db.calculate_combo_stats(blade, ratchet, bit)

            # Grounding context for Gemini
            grounding_data = (
                f"【選手指定測試搭配】：{combo_stats['combo_name']} ({combo_stats['combo_name_zh']})\n"
                f"- 刃 (Blade)：{blade['name']} ({blade['name_zh']}) | 系列：{blade['series']} | 重量：{blade['weight_g']}g | 重心：{blade['cg']} | 特性：{blade['description']}\n"
                f"- 墊片 (Ratchet)：{ratchet['name']} | 高度：{ratchet['height_mm']}mm | 齒數：{ratchet['blades_count']} | 重量：{ratchet['weight_g']}g | 抗爆特性：{ratchet['burst_resistance']} | 戰術影響：{ratchet['tactical_effect']}\n"
                f"- 軸點 (Bit)：{bit['name']} | 類型：{bit['type']} | 重量：{bit['weight_g']}g | 齒數：{bit['gear_teeth']} | X-Dash 特性：{bit['x_dash_capability']} | 物理機制：{bit['description']} | 戰術影響：{bit['tactical_effect']}\n"
                f"- 物理總重：{combo_stats['total_weight_g']}g\n"
                f"- 系統預估四維數值：攻擊力 {combo_stats['scores']['attack']}, 持久力 {combo_stats['scores']['stamina']}, 防禦力 {combo_stats['scores']['defense']}, X-Dash 突襲率 {combo_stats['scores']['xdash']}\n"
            )

            # Community insights grounding
            matched_insights = self.find_relevant_insights(user_text, [blade, ratchet, bit])
            insights_context = self._format_insights_context(matched_insights)

            prompt = (
                f"【實體遙測數據庫輸出】：\n{grounding_data}\n"
                f"{insights_context}\n"
                f"【選手戰術提問】：\n{user_text}\n\n"
                f"請以世界大賽戰術教練與改裝大師的專業身分，根據上述真實規格數據與社群情報，對此搭配執行四大維度的深度專業拆解，"
                f"給出具體的改裝微調建議與發射戰術指引！"
            )

            coach_text = self._call_gemini_api(prompt)
            flex_msg = FlexMessageBuilder.build_combo_dashboard(
                combo_stats=combo_stats,
                coach_analysis=coach_text
            )

            return {
                "reply_text": coach_text,
                "flex_message": flex_msg,
                "combo_stats": combo_stats,
                "part_info": None
            }

        # Step 2: Check if user is asking about a single component
        single_part = db.find_part(user_text.strip())
        if not single_part:
            for candidate_token in user_text.split():
                single_part = db.find_part(candidate_token)
                if single_part:
                    break

        if single_part:
            matched_insights = self.find_relevant_insights(user_text, [single_part])
            insights_context = self._format_insights_context(matched_insights)

            prompt = (
                f"選手正在詢問部件：{single_part.get('name')} {single_part.get('name_zh', '')}\n"
                f"規格資料：重量 {single_part.get('weight_g')}g, 類型 {single_part.get('type')}, 描述：{single_part.get('description', '')}\n"
                f"{insights_context}\n"
                f"選手原話：{user_text}\n"
                f"請以改裝大師的身分深度剖析這個部件在現行賽事環境中的改裝適配性與戰術定位。"
            )
            coach_text = self._call_gemini_api(prompt)
            flex_msg = FlexMessageBuilder.build_part_card(single_part)
            return {
                "reply_text": coach_text,
                "flex_message": flex_msg,
                "combo_stats": None,
                "part_info": single_part
            }

        # Step 3: General strategic guidance or tactical inquiry
        matched_insights = self.find_relevant_insights(user_text)
        insights_context = self._format_insights_context(matched_insights)
        prompt = f"{insights_context}\n選手原話：{user_text}\n請以世界大賽戰術教練身分給出專業戰術解答。" if insights_context else user_text
        coach_text = self._call_gemini_api(prompt)
        return {
            "reply_text": coach_text,
            "flex_message": None,
            "combo_stats": None,
            "part_info": None
        }

coach_engine = BeybladeCoachEngine()
