import time
import logging
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger("session_manager")

SESSION_TIMEOUT_SECONDS = 1800  # 30 minutes

class SessionState:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.last_activity = time.time()
        self.last_combo: Optional[Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]] = None
        self.history: List[Dict[str, str]] = []  # List of {"role": "user"|"assistant", "text": str}

    def is_expired(self) -> bool:
        return (time.time() - self.last_activity) > SESSION_TIMEOUT_SECONDS

    def touch(self):
        self.last_activity = time.time()

    def add_turn(self, user_text: str, assistant_text: str):
        self.touch()
        self.history.append({"role": "user", "text": user_text})
        self.history.append({"role": "assistant", "text": assistant_text})
        # Keep only the last 6 messages (3 full turns)
        if len(self.history) > 6:
            self.history = self.history[-6:]

    def set_combo(self, blade: Dict[str, Any], ratchet: Dict[str, Any], bit: Dict[str, Any]):
        self.last_combo = (blade, ratchet, bit)

    def get_combo_name(self) -> Optional[str]:
        if self.last_combo:
            b, r, bit = self.last_combo
            return f"{b.get('name_zh') or b.get('name')} {r.get('name')} {bit.get('name')}"
        return None

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}

    def get_session(self, user_id: str) -> SessionState:
        if not user_id:
            user_id = "default_user"
        
        session = self.sessions.get(user_id)
        if session is None or session.is_expired():
            if session and session.is_expired():
                logger.info(f"Session for user {user_id} expired after 30 mins of inactivity. Resetting.")
            session = SessionState(user_id)
            self.sessions[user_id] = session
        else:
            session.touch()
        return session

    def update_session(self, user_id: str, user_text: str, reply_text: str, combo: Optional[Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]] = None):
        session = self.get_session(user_id)
        session.add_turn(user_text, reply_text)
        if combo:
            session.set_combo(combo[0], combo[1], combo[2])

    def clear_session(self, user_id: str):
        if not user_id:
            user_id = "default_user"
        if user_id in self.sessions:
            logger.info(f"Explicitly clearing session for user {user_id}")
            del self.sessions[user_id]

session_manager = SessionManager()
