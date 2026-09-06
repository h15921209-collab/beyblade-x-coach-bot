import unittest
from core.coach_engine import coach_engine
from core.flex_builder import FlexMessageBuilder
from core.database import db

class TestCoachEngine(unittest.TestCase):
    def test_analyze_full_combo(self):
        result = coach_engine.analyze("教練，幫我測試 Phoenix Wing 9-60O")
        self.assertIsNotNone(result)
        self.assertIn("reply_text", result)
        self.assertTrue(len(result["reply_text"]) > 50)
        self.assertIsNotNone(result["flex_message"])
        self.assertEqual(result["flex_message"]["type"], "flex")

        stats = result.get("combo_stats")
        self.assertIsNotNone(stats)
        self.assertEqual(stats["combo_name"], "Phoenix Wing 9-60O")

    def test_flex_message_structure(self):
        b = db.find_blade("phoenix_wing")
        r = db.find_ratchet("9-60")
        bit = db.find_bit("O")
        stats = db.calculate_combo_stats(b, r, bit)

        flex_msg = FlexMessageBuilder.build_combo_dashboard(stats, "戰術測試點評")
        self.assertEqual(flex_msg["type"], "flex")
        self.assertIn("contents", flex_msg)
        contents = flex_msg["contents"]
        self.assertEqual(contents["type"], "bubble")
        self.assertIn("header", contents)
        self.assertIn("hero", contents)
        self.assertIn("body", contents)

    def test_single_part_inquiry(self):
        result = coach_engine.analyze("9-60")
        self.assertIsNotNone(result)
        self.assertIsNotNone(result["part_info"])
        self.assertEqual(result["part_info"]["name"], "9-60")
        self.assertIsNotNone(result["flex_message"])

if __name__ == "__main__":
    unittest.main()
