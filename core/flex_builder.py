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
        blade = combo_stats.get("blade", {})
        ratchet = combo_stats.get("ratchet", {})
        bit = combo_stats.get("bit", {})

        hero_img = blade.get("card_image_url") or combo_stats.get("hero_image_url") or "https://beyblade-x-coach-bot.onrender.com/static/images/blade_phoenix_wing.png"
        if hero_img.startswith("/"):
            hero_img = f"https://beyblade-x-coach-bot.onrender.com{hero_img}"

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
        img_url = part.get("card_image_url") or part.get("image_url") or part.get("image_local") or "https://beyblade-x-coach-bot.onrender.com/static/images/blade_phoenix_wing.png"
        if img_url.startswith("/"):
            img_url = f"https://beyblade-x-coach-bot.onrender.com{img_url}"
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

    @classmethod
    def build_combos_carousel(
        cls,
        combos_stats: List[Dict[str, Any]],
        category_title: str = "熱門戰術推薦"
    ) -> Dict[str, Any]:
        """
        Builds a Carousel Flex Message containing multiple combo bubbles.
        """
        bubbles = []
        for combo_stats in combos_stats:
            combo_name = combo_stats.get("combo_name", "")
            combo_name_zh = combo_stats.get("combo_name_zh", "")
            total_weight = combo_stats.get("total_weight_g", 0.0)
            scores = combo_stats.get("scores", {"attack": 70, "stamina": 70, "defense": 70, "xdash": 70})
            blade = combo_stats.get("blade", {})
            ratchet = combo_stats.get("ratchet", {})
            bit = combo_stats.get("bit", {})

            hero_img = blade.get("card_image_url") or combo_stats.get("hero_image_url") or "https://beyblade-x-coach-bot.onrender.com/static/images/blade_phoenix_wing.png"
            if hero_img.startswith("/"):
                hero_img = f"https://beyblade-x-coach-bot.onrender.com{hero_img}"

            bubble = {
                "type": "bubble",
                "size": "mega",
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
                                {"type": "text", "text": category_title.upper(), "weight": "bold", "color": "#00E5FF", "size": "xxs"},
                                {"type": "text", "text": f"總重 {total_weight}g", "color": "#FFD700", "size": "xxs", "align": "end", "weight": "bold"}
                            ]
                        },
                        {
                            "type": "text",
                            "text": combo_name.upper(),
                            "weight": "bold",
                            "size": "md",
                            "color": "#FFFFFF",
                            "margin": "xs"
                        },
                        {
                            "type": "text",
                            "text": combo_name_zh,
                            "size": "xxs",
                            "color": "#94A3B8"
                        }
                    ]
                },
                "hero": {
                    "type": "image",
                    "url": hero_img,
                    "size": "full",
                    "aspectRatio": "16:11",
                    "aspectMode": "fit",
                    "action": {"type": "uri", "uri": hero_img}
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        cls._create_bar("攻擊破壞力", scores.get("attack", 70), "#FF3B30"),
                        cls._create_bar("極致持久力", scores.get("stamina", 70), "#34C759"),
                        cls._create_bar("防禦抗爆力", scores.get("defense", 70), "#007AFF"),
                        cls._create_bar("X-Dash 突襲率", scores.get("xdash", 70), "#FF9500"),
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
                                    "paddingAll": "4px",
                                    "margin": "xs",
                                    "flex": 1,
                                    "contents": [
                                        {"type": "text", "text": "刃", "size": "xxs", "color": "#718096"},
                                        {"type": "text", "text": f"{blade.get('name_zh', blade.get('name', ''))[:5]}", "size": "xxs", "color": "#FFFFFF", "weight": "bold"}
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "backgroundColor": "#1A202C",
                                    "cornerRadius": "4px",
                                    "paddingAll": "4px",
                                    "margin": "xs",
                                    "flex": 1,
                                    "contents": [
                                        {"type": "text", "text": "墊片", "size": "xxs", "color": "#718096"},
                                        {"type": "text", "text": f"{ratchet.get('name', '')}", "size": "xxs", "color": "#FFFFFF", "weight": "bold"}
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "backgroundColor": "#1A202C",
                                    "cornerRadius": "4px",
                                    "paddingAll": "4px",
                                    "margin": "xs",
                                    "flex": 1,
                                    "contents": [
                                        {"type": "text", "text": "軸點", "size": "xxs", "color": "#718096"},
                                        {"type": "text", "text": f"{bit.get('name', '').split()[0]}", "size": "xxs", "color": "#FFFFFF", "weight": "bold"}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#0284C7",
                            "height": "sm",
                            "action": {
                                "type": "message",
                                "label": "⚡ 深入剖析這組戰術",
                                "text": f"選手，請為我深入拆解【{combo_name}】在現行賽事中的打法與發射手法！"
                            }
                        }
                    ]
                }
            }
            bubbles.append(bubble)

        return {
            "type": "flex",
            "altText": f"【戰術輪播】：{category_title}",
            "contents": {
                "type": "carousel",
                "contents": bubbles
            }
        }

    @classmethod
    def build_videos_carousel(cls, videos: List[Dict[str, Any]], topic: str = "實戰精選") -> Dict[str, Any]:
        """
        Builds a horizontal carousel of YouTube video recommendation cards.
        """
        if not videos:
            return {}

        bubbles = []
        for vid in videos[:5]:
            title = vid.get("title", "戰鬥陀螺 X 實戰精華")
            channel = vid.get("channel", "YouTube 精選")
            duration = vid.get("duration", "精彩實況")
            url = vid.get("url", "https://www.youtube.com")
            thumb = vid.get("thumbnail", "https://img.youtube.com/vi/default/hqdefault.jpg")

            bubble = {
                "type": "bubble",
                "size": "kilo",
                "styles": {
                    "body": {"backgroundColor": "#0B0F19"},
                    "footer": {"backgroundColor": "#0B0F19"}
                },
                "hero": {
                    "type": "image",
                    "url": thumb,
                    "size": "full",
                    "aspectRatio": "16:9",
                    "aspectMode": "cover",
                    "action": {
                        "type": "uri",
                        "label": "Watch Video",
                        "uri": url
                    }
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "12px",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "▶ YouTube 實戰",
                                    "size": "xxs",
                                    "color": "#FF0000",
                                    "weight": "bold",
                                    "flex": 3
                                },
                                {
                                    "type": "text",
                                    "text": duration,
                                    "size": "xxs",
                                    "color": "#A0AEC0",
                                    "align": "end",
                                    "flex": 2
                                }
                            ]
                        },
                        {
                            "type": "text",
                            "text": title,
                            "weight": "bold",
                            "size": "sm",
                            "color": "#FFFFFF",
                            "wrap": True,
                            "maxLines": 2,
                            "margin": "sm"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "margin": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"頻道：{channel}",
                                    "size": "xxs",
                                    "color": "#718096",
                                    "wrap": False,
                                    "flex": 1
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "8px",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#FF0000",
                            "height": "sm",
                            "action": {
                                "type": "uri",
                                "label": "▶️ 立即在 YouTube 觀看",
                                "uri": url
                            }
                        }
                    ]
                }
            }
            bubbles.append(bubble)

        return {
            "type": "flex",
            "altText": f"🎬 【實戰影片推薦】：{topic}",
            "contents": {
                "type": "carousel",
                "contents": bubbles
            }
        }

    @classmethod
    def build_vs_dashboard(cls, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds an esports arena-style VS Battle Dashboard Flex Message.
        """
        combo_a = match_data["combo_a"]
        combo_b = match_data["combo_b"]
        w_a = match_data["win_rate_a"]
        w_b = match_data["win_rate_b"]
        finish = match_data["finish_breakdown"]
        advice = match_data["tactical_advice"]

        name_a = combo_a.get("combo_name_zh") or combo_a["combo_name"]
        name_b = combo_b.get("combo_name_zh") or combo_b["combo_name"]
        weight_a = combo_a.get("total_weight_g", 43.0)
        weight_b = combo_b.get("total_weight_g", 43.0)
        img_a = combo_a.get("hero_image_url") or "https://beyblade-x-coach-bot.onrender.com/static/images/blades/phoenix_wing.png"
        img_b = combo_b.get("hero_image_url") or "https://beyblade-x-coach-bot.onrender.com/static/images/blades/wizard_rod.png"

        bubble = {
            "type": "bubble",
            "size": "giga",
            "styles": {
                "header": {"backgroundColor": "#0B0F19"},
                "body": {"backgroundColor": "#0F172A"},
                "footer": {"backgroundColor": "#0B0F19"}
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
                                "text": "⚔️ 戰鬥陀螺 X 宿命對決推演",
                                "weight": "bold",
                                "size": "md",
                                "color": "#FFD700",
                                "flex": 4
                            },
                            {
                                "type": "text",
                                "text": "VS ARENA",
                                "size": "xxs",
                                "color": "#00E5FF",
                                "weight": "bold",
                                "align": "end",
                                "flex": 2
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "text": "PHYSICAL IMPACT & WIN RATE PREDICTION",
                        "size": "xxs",
                        "color": "#718096",
                        "margin": "xs"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "14px",
                "contents": [
                    # 1. Red Corner vs Blue Corner Cards
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [
                            # Red Corner
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 5,
                                "backgroundColor": "#1E1B2E",
                                "cornerRadius": "8px",
                                "paddingAll": "8px",
                                "borderColor": "#EF4444",
                                "borderWidth": "1px",
                                "contents": [
                                    {
                                        "type": "image",
                                        "url": img_a,
                                        "size": "full",
                                        "aspectRatio": "1:1",
                                        "aspectMode": "fit"
                                    },
                                    {
                                        "type": "text",
                                        "text": "🔴 紅角",
                                        "size": "xxs",
                                        "color": "#EF4444",
                                        "weight": "bold",
                                        "margin": "xs"
                                    },
                                    {
                                        "type": "text",
                                        "text": name_a,
                                        "size": "xs",
                                        "color": "#FFFFFF",
                                        "weight": "bold",
                                        "wrap": True,
                                        "maxLines": 2
                                    },
                                    {
                                        "type": "text",
                                        "text": f"⚖️ {weight_a}g",
                                        "size": "xxs",
                                        "color": "#A0AEC0",
                                        "margin": "xs"
                                    }
                                ]
                            },
                            # VS Badge
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "justifyContent": "center",
                                "alignItems": "center",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "VS",
                                        "size": "xl",
                                        "weight": "bold",
                                        "color": "#FFD700"
                                    },
                                    {
                                        "type": "text",
                                        "text": "對決",
                                        "size": "xxs",
                                        "color": "#718096"
                                    }
                                ]
                            },
                            # Blue Corner
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 5,
                                "backgroundColor": "#132338",
                                "cornerRadius": "8px",
                                "paddingAll": "8px",
                                "borderColor": "#0284C7",
                                "borderWidth": "1px",
                                "contents": [
                                    {
                                        "type": "image",
                                        "url": img_b,
                                        "size": "full",
                                        "aspectRatio": "1:1",
                                        "aspectMode": "fit"
                                    },
                                    {
                                        "type": "text",
                                        "text": "🔵 藍角",
                                        "size": "xxs",
                                        "color": "#38BDF8",
                                        "weight": "bold",
                                        "margin": "xs"
                                    },
                                    {
                                        "type": "text",
                                        "text": name_b,
                                        "size": "xs",
                                        "color": "#FFFFFF",
                                        "weight": "bold",
                                        "wrap": True,
                                        "maxLines": 2
                                    },
                                    {
                                        "type": "text",
                                        "text": f"⚖️ {weight_b}g",
                                        "size": "xxs",
                                        "color": "#A0AEC0",
                                        "margin": "xs"
                                    }
                                ]
                            }
                        ]
                    },
                    # 2. Win Rate Bar
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"🔴 紅方勝率 {w_a}%",
                                        "size": "xs",
                                        "color": "#EF4444",
                                        "weight": "bold",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": f"藍方勝率 {w_b}% 🔵",
                                        "size": "xs",
                                        "color": "#38BDF8",
                                        "weight": "bold",
                                        "align": "end",
                                        "flex": 1
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "margin": "sm",
                                "height": "10px",
                                "backgroundColor": "#1E293B",
                                "cornerRadius": "5px",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "width": f"{w_a}%",
                                        "backgroundColor": "#EF4444",
                                        "cornerRadius": "5px",
                                        "contents": []
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "width": f"{w_b}%",
                                        "backgroundColor": "#0284C7",
                                        "cornerRadius": "5px",
                                        "contents": []
                                    }
                                ]
                            }
                        ]
                    },
                    # 3. Finish Distribution Breakdown
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "backgroundColor": "#182234",
                        "cornerRadius": "6px",
                        "paddingAll": "10px",
                        "contents": [
                            {
                                "type": "text",
                                "text": "📊 預估終結方式機率分佈",
                                "size": "xs",
                                "color": "#FFD700",
                                "weight": "bold"
                            },
                            cls._create_bar("💥 擊出戰場 (Over/Extreme)", finish.get("over", 35), "#F59E0B"),
                            cls._create_bar("⚡ 爆裂擊破 (Burst Finish)", finish.get("burst", 20), "#EF4444"),
                            cls._create_bar("🌀 迴轉持久 (Spin Finish)", finish.get("spin", 45), "#10B981")
                        ]
                    },
                    # 4. Tactical Advice Box
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "backgroundColor": "#1E1B2E",
                        "borderColor": "#A855F7",
                        "borderWidth": "1px",
                        "cornerRadius": "6px",
                        "paddingAll": "10px",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🎯 教練克敵發射手勢指引",
                                "size": "xs",
                                "color": "#C084FC",
                                "weight": "bold"
                            },
                            {
                                "type": "text",
                                "text": advice.get("corner_a", ""),
                                "size": "xs",
                                "color": "#E2E8F0",
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
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#0284C7",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": f"🎬 觀看這場實戰對決影片",
                            "text": f"請為我搜尋【{name_a} VS {name_b}】的最新實戰對戰影片！"
                        }
                    }
                ]
            }
        }

        return {
            "type": "flex",
            "altText": f"⚔️ 【對決推演】：{name_a} VS {name_b}",
            "contents": bubble
        }


