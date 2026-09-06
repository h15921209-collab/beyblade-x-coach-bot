import unittest
from core.database import db

class TestBeybladeDatabase(unittest.TestCase):
    def test_load_parts(self):
        self.assertGreater(len(db.blades), 10)
        self.assertGreater(len(db.ratchets), 5)
        self.assertGreater(len(db.bits), 8)

    def test_find_blade(self):
        pw = db.find_blade("Phoenix Wing")
        self.assertIsNotNone(pw)
        self.assertEqual(pw["id"], "phoenix_wing")
        self.assertAlmostEqual(pw["weight_g"], 38.8, places=1)

        # Chinese name lookup
        wr = db.find_blade("魔導權杖")
        self.assertIsNotNone(wr)
        self.assertEqual(wr["id"], "wizard_rod")

    def test_find_ratchet(self):
        r960 = db.find_ratchet("9-60")
        self.assertIsNotNone(r960)
        self.assertEqual(r960["blades_count"], 9)

        r560 = db.find_ratchet("560")
        self.assertIsNotNone(r560)
        self.assertEqual(r560["name"], "5-60")

    def test_find_bit(self):
        bit_f = db.find_bit("F")
        self.assertIsNotNone(bit_f)
        self.assertEqual(bit_f["type"], "Attack")

        bit_b = db.find_bit("Ball")
        self.assertIsNotNone(bit_b)
        self.assertEqual(bit_b["id"], "B")

    def test_parse_combo_from_text(self):
        combo1 = db.parse_combo_from_text("我想測試 Phoenix Wing 9-60O")
        self.assertIsNotNone(combo1)
        b, r, bit = combo1
        self.assertEqual(b["id"], "phoenix_wing")
        self.assertEqual(r["id"], "9-60")
        self.assertEqual(bit["id"], "O")

        combo2 = db.parse_combo_from_text("魔導權杖 7-60 B 怎麼樣？")
        self.assertIsNotNone(combo2)
        b2, r2, bit2 = combo2
        self.assertEqual(b2["id"], "wizard_rod")
        self.assertEqual(r2["id"], "7-60")
        self.assertEqual(bit2["id"], "B")

    def test_calculate_combo_stats(self):
        b = db.find_blade("phoenix_wing")
        r = db.find_ratchet("9-60")
        bit = db.find_bit("O")
        stats = db.calculate_combo_stats(b, r, bit)

        self.assertEqual(stats["combo_name"], "Phoenix Wing 9-60O")
        self.assertGreater(stats["total_weight_g"], 45.0)
        self.assertIn("attack", stats["scores"])
        self.assertIn("stamina", stats["scores"])
        self.assertIn("defense", stats["scores"])
        self.assertIn("xdash", stats["scores"])
        self.assertTrue(stats["hero_image_url"].startswith("http"))

if __name__ == "__main__":
    unittest.main()
