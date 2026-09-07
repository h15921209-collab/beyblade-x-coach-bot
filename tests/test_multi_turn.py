import unittest
import time
from core.coach_engine import coach_engine
from core.session_manager import session_manager, SessionState
from core.database import db

class TestMultiTurnSession(unittest.TestCase):
    def setUp(self):
        self.user_id = 'test_user_dual_track'
        session_manager.clear_session(self.user_id)

    def test_multi_turn_and_part_swap(self):
        # Turn 1: User introduces initial combo
        session = session_manager.get_session(self.user_id)
        msg1 = '鳳凰飛翼 9-60O'
        res1 = coach_engine.analyze(msg1, session=session)
        
        self.assertIsNotNone(res1.get('combo_stats'))
        self.assertEqual(res1['combo_stats']['combo_name'], 'Phoenix Wing 9-60O')
        self.assertEqual(res1['combo_tuple'][0]['name'], 'Phoenix Wing')
        self.assertEqual(res1['combo_tuple'][1]['name'], '9-60')
        self.assertEqual(res1['combo_tuple'][2]['id'], 'O')

        # Update session state as web/app.py does
        session_manager.update_session(
            user_id=self.user_id,
            user_text=msg1,
            reply_text=res1['reply_text'],
            combo=res1['combo_tuple']
        )

        session = session_manager.get_session(self.user_id)
        self.assertIsNotNone(session.last_combo)
        self.assertEqual(len(session.history), 2)

        # Turn 2: User asks follow-up swap for ratchet (5-60)
        msg2 = '那如果換成 5-60 呢？'
        res2 = coach_engine.analyze(msg2, session=session)
        
        self.assertTrue(res2.get('is_swap'))
        self.assertIsNotNone(res2.get('combo_stats'))
        self.assertEqual(res2['combo_stats']['combo_name'], 'Phoenix Wing 5-60O')
        self.assertEqual(res2['combo_tuple'][1]['name'], '5-60')
        self.assertIsNotNone(res2.get('flex_message'))

        session_manager.update_session(
            user_id=self.user_id,
            user_text=msg2,
            reply_text=res2['reply_text'],
            combo=res2['combo_tuple']
        )

        # Turn 3: User asks follow-up swap for bit (Ball)
        session = session_manager.get_session(self.user_id)
        msg3 = '改用 Ball 軸呢？'
        res3 = coach_engine.analyze(msg3, session=session)
        
        self.assertTrue(res3.get('is_swap'))
        self.assertIsNotNone(res3.get('combo_stats'))
        self.assertEqual(res3['combo_stats']['combo_name'], 'Phoenix Wing 5-60B')
        self.assertEqual(res3['combo_tuple'][2]['id'], 'B')

        session_manager.update_session(
            user_id=self.user_id,
            user_text=msg3,
            reply_text=res3['reply_text'],
            combo=res3['combo_tuple']
        )

        # Turn 4: User asks follow-up swap for blade (魔導神杖)
        session = session_manager.get_session(self.user_id)
        msg4 = '換成魔導神杖呢？'
        res4 = coach_engine.analyze(msg4, session=session)
        
        self.assertTrue(res4.get('is_swap'))
        self.assertIsNotNone(res4.get('combo_stats'))
        self.assertEqual(res4['combo_stats']['combo_name'], 'Wizard Rod 5-60B')
        self.assertEqual(res4['combo_tuple'][0]['name'], 'Wizard Rod')

        # Turn 5: User asks contextual follow-up question
        session_manager.update_session(
            user_id=self.user_id,
            user_text=msg4,
            reply_text=res4['reply_text'],
            combo=res4['combo_tuple']
        )
        session = session_manager.get_session(self.user_id)
        msg5 = '那它的主要弱點是什麼？'
        res5 = coach_engine.analyze(msg5, session=session)
        self.assertFalse(res5.get('is_swap'))
        self.assertIsNotNone(res5.get('combo_tuple'))
        self.assertEqual(res5['combo_tuple'][0]['name'], 'Wizard Rod')

    def test_session_reset(self):
        session = session_manager.get_session(self.user_id)
        b = db.find_blade('phoenix_wing')
        r = db.find_ratchet('9-60')
        bit = db.find_bit('O')
        session_manager.update_session(self.user_id, 'test', 'reply', combo=(b, r, bit))

        s_before = session_manager.get_session(self.user_id)
        self.assertIsNotNone(s_before.last_combo)

        session_manager.clear_session(self.user_id)

        s_after = session_manager.get_session(self.user_id)
        self.assertIsNone(s_after.last_combo)
        self.assertEqual(len(s_after.history), 0)

    def test_session_timeout(self):
        session = session_manager.get_session(self.user_id)
        b = db.find_blade('phoenix_wing')
        r = db.find_ratchet('9-60')
        bit = db.find_bit('O')
        session_manager.update_session(self.user_id, 'test', 'reply', combo=(b, r, bit))

        session.last_activity = time.time() - 1900
        self.assertTrue(session.is_expired())

        new_session = session_manager.get_session(self.user_id)
        self.assertIsNone(new_session.last_combo)
        self.assertEqual(len(new_session.history), 0)

if __name__ == '__main__':
    unittest.main()
