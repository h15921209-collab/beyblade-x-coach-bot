from typing import Dict, Any, List

class FlexMessageBuilder:
    @staticmethod
    def _create_bar(label: str, score: int, color: str) -> Dict[str, Any]:
        """
        Creates a stat bar item with label, progress bar and score percentage
        """
        return {
            "type": "box",
            "layout": "vertical",
            "margin": "md",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": label,
                            "size": "xs",
                            "color": "#aaaaaa",
                            "flex": 4
                        },
                        {
                            "type": "text",
                            "text": f"{score}/100",
                            "size": "xs",
                            "color": "#ffffff",
                            "align": "end",
                            "weight": "bold",
                            "flex": 2
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "xs",
                    "height": "6px",
                    "backgroundColor": "#2A2E39",
                    "cornerRadius": "3px",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "width": f"{score}%",
                            "backgroundColor": color,
                            "cornerRadius": "3px",
                            "contents": []
                        }
                    ]
                }
            ]
        }

    @classmethod
    def build_combo_dashboard(
        cls,
        combo_stats: Dict[str, Any],
        coach_analysis: str,
        quick_tips: List[str] = None
    ) -> Dict[str, Any]:
        """
        Builds a high-tech esports style LINE Flex Message bubble for a Beyblade combination.
        """
        combo_name = combo_stats.get("combo_name", "CUSTOM BEYBLADE")
        combo_name_zh = combo_stats.get("combo_name_zh", "")
        total_weight = combo_stats.get("total_weight_g", 0.0)
        scores = combo_stats.get("scores", {"attack": 70, "stamina": 70, "defense": 70, "xdash": 70})
        hero_img = combo_stats.get("hero_image_url") or "https://static.wikia.nocookie.net/beyblade/images/d/d3/Phoenix_Wing_9-60GF.png"
        
        blade = combo_stats.get("blade", {})
        ratchet = combo_stats.get("ratchet", {})
        bit = combo_stats.get("bit", {})

        # Truncate coach text if too long for card preview
        display_analysis = coach_analysis[:350] + "..." if len(coach_analysis) > 350 else coach_analysis

        bubble = {
            "type": "bubble",
            "size": "giga",
            "styles": {
                "header": {"backgroundColor": "#0F141C"},
                "hero": {"backgroundColor": "#0A0D14"},
                "body": {"backgroundColor": "#131822"},
                "footer": {"backgroundColor": "#0F141C"}
            },
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "BEYBLADE X 戰術戰報",
                                "weight": "bold",
                                "color": "#00E5FF",
                                "size": "xs",
                                "letterSpacing": "2px"
                            },
                            {
                                "type": "text",
                                "text": f"總重 {total_weight}g",
                                "color": "#FFD700",
                                "size": "xs",
                                "align": "end",
                                "weight": "bold"
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "text": combo_name.upper(),
                        "weight": "bold",
                        "size": "lg",
                        "color": "#FFFFFF",
                        "margin": "xs"
                    },
                    {
                        "type": "text",
                        "text": f"{combo_name_zh} | 階級：{blade.get('tier', 'A')} 級主流",
                        "size": "xs",
                        "color": "#8E99A8"
                    }
                ]
            },
            "hero": {
                "type": "image",
                "url": hero_img,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "fit",
                "action": {
                    "type": "uri",
                    "uri": hero_img
                }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    # 1. 四維戰力指標
                    {
                        "type": "text",
                        "text": "四維戰力與物理參數拆解",
                        "size": "xs",
                        "weight": "bold",
                        "color": "#00E5FF"
                    },
                    cls._create_bar("攻擊力 (Attack)", scores.get("attack", 50), "#FF3B30"),
                    cls._create_bar("持久力 (Stamina)", scores.get("stamina", 50), "#34C759"),
                    cls._create_bar("防禦抗爆 (Defense)", scores.get("defense", 50), "#007AFF"),
                    cls._create_bar("極速線突襲 (X-Dash)", scores.get("xdash", 50), "#FF9500"),

                    # 分隔線
                    {"type": "separator", "margin": "lg", "color": "#2A2E39"},

                    # 2. 部件規格標籤
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "backgroundColor": "#1A202C",
                                "cornerRadius": "4px",
                                "paddingAll": "6px",
                                "flex": 1,
                                "contents": [
                                    {"type": "text", "text": "刃 BLADE", "size": "xxs", "color": "#718096"},
                                    {"type": "text", "text": f"{blade.get('name', '')}", "size": "xxs", "color": "#FFFFFF", "weight": "bold"},
                                    {"type": "text", "text": f"{blade.get('weight_g', 0)}g", "size": "xxs", "color": "#A0AEC0"}
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "backgroundColor": "#1A202C",
                                "cornerRadius": "4px",
                                "paddingAll": "6px",
                                "margin": "xs",
                                "flex": 1,
                                "contents": [
                                    {"type": "text", "text": "墊片 RATCHET", "size": "xxs", "color": "#718096"},
                                    {"type": "text", "text": f"{ratchet.get('name', '')}", "size": "xxs", "color": "#FFFFFF", "weight": "bold"},
                                    {"type": "text", "text": f"{ratchet.get('weight_g', 0)}g", "size": "xxs", "color": "#A0AEC0"}
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "backgroundColor": "#1A202C",
                                "cornerRadius": "4px",
                                "paddingAll": "6px",
                                "margin": "xs",
                                "flex": 1,
                                "contents": [
                                    {"type": "text", "text": "軸點 BIT", "size": "xxs", "color": "#718096"},
                                    {"type": "text", "text": f"{bit.get('name', '')}", "size": "xxs", "color": "#FFFFFF", "weight": "bold"},
                                    {"type": "text", "text": f"{bit.get('weight_g', 0)}g", "size": "xxs", "color": "#A0AEC0"}
                                ]
                            }
                        ]
                    },

                    # 3. 教練戰術解析
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "backgroundColor": "#18202F",
                        "cornerRadius": "6px",
                        "paddingAll": "10px",
                        "contents": [
                            {
                                "type": "text",
                                "text": "戰術教練點評：",
                                "size": "xs",
                                "weight": "bold",
                                "color": "#FFCC00"
                            },
                            {
                                "type": "text",
                                "text": display_analysis,
                                "size": "xxs",
                                "color": "#CBD5E1",
                                "wrap": True,
                                "margin": "xs"
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "secondary",
                        "color": "#2D3748",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": "改裝 5-60 差異",
                            "text": f"如果把 {combo_name} 的墊片改為 5-60，會有什麼物理改變？"
                        }
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#0052CC",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": "打 Wizard Rod",
                            "text": f"這組 {combo_name} 面對主流 Wizard Rod 9-60B 勝率與克制打法如何？"
                        }
                    }
                ]
            }
        }
        return {"type": "flex", "altText": f"戰術戰報：{combo_name}", "contents": bubble}

    @classmethod
    def build_part_card(cls, part: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a dedicated Flex card for a single component.
        """
        name = part.get("name", "Unknown Part")
        name_zh = part.get("name_zh", "")
        category = part.get("_category") or part.get("type", "Component")
        weight = part.get("weight_g", 0.0)
        img_url = part.get("image_url") or "https://static.wikia.nocookie.net/beyblade/images/d/d3/Phoenix_Wing_9-60GF.png"
        desc = part.get("description") or part.get("tactical_effect", "")

        bubble = {
            "type": "bubble",
            "size": "kilo",
            "styles": {
                "header": {"backgroundColor": "#0F141C"},
                "hero": {"backgroundColor": "#0A0D14"},
                "body": {"backgroundColor": "#131822"}
            },
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"BEYBLADE X 部件檔案庫 [{category.upper()}]",
                        "weight": "bold",
                        "color": "#00E5FF",
                        "size": "xxs"
                    },
                    {
                        "type": "text",
                        "text": f"{name} {name_zh}",
                        "weight": "bold",
                        "size": "md",
                        "color": "#FFFFFF"
                    },
                    {
                        "type": "text",
                        "text": f"規格淨重：約 {weight}g | 階級評定：{part.get('tier', 'A')}",
                        "size": "xxs",
                        "color": "#A0AEC0"
                    }
                ]
            },
            "hero": {
                "type": "image",
                "url": img_url,
                "size": "full",
                "aspectRatio": "16:11",
                "aspectMode": "fit",
                "action": {
                    "type": "uri",
                    "uri": img_url
                }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "物理特性與實戰指引：",
                        "size": "xs",
                        "weight": "bold",
                        "color": "#FFD700"
                    },
                    {
                        "type": "text",
                        "text": desc,
                        "size": "xs",
                        "color": "#E2E8F0",
                        "wrap": True,
                        "margin": "xs"
                    }
                ]
            }
        }
        return {"type": "flex", "altText": f"部件圖鑑：{name}", "contents": bubble}
