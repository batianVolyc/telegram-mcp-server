"""Session management"""
import os
import time
import json
import fcntl
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

# Shared session storage file
SESSION_STORAGE_FILE = os.path.expanduser("~/.claude/telegram-mcp-sessions.json")

class Session:
    """Represents a Claude Code session"""

    def __init__(self, session_id: str, project_path: str, chat_id: str):
        self.session_id = session_id
        self.project_path = project_path
        self.chat_id = chat_id
        self.status = "running"  # running, waiting, idle
        self.created_at = datetime.now().isoformat()
        self.last_active = datetime.now().isoformat()
        self.last_message = None
        self.pending_reply = False

    def update_activity(self):
        """Update last active timestamp"""
        self.last_active = datetime.now().isoformat()
        # Note: Will be saved to file by registry.update_session()

    def set_waiting(self):
        """Mark session as waiting for user reply"""
        self.status = "waiting"
        self.pending_reply = True
        self.update_activity()
        # Note: Will be saved to file by registry.update_session()

    def set_running(self):
        """Mark session as running"""
        self.status = "running"
        self.pending_reply = False
        self.update_activity()
        # Note: Will be saved to file by registry.update_session()

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "project_path": self.project_path,
            "chat_id": self.chat_id,
            "status": self.status,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "last_message": self.last_message,
            "pending_reply": self.pending_reply
        }


class SessionRegistry:
    """Global session registry with shared file storage"""

    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.storage_file = SESSION_STORAGE_FILE

        # Ensure storage directory exists
        storage_dir = os.path.dirname(self.storage_file)
        os.makedirs(storage_dir, exist_ok=True)

        # Load existing sessions from file
        self._load_from_file()

    def _load_from_file(self):
        """Load sessions from shared file"""
        if not os.path.exists(self.storage_file):
            return

        try:
            with open(self.storage_file, 'r') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # Shared lock for reading
                data = json.load(f)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # Reconstruct sessions from data
            for sid, sess_data in data.items():
                session = Session(
                    sess_data['session_id'],
                    sess_data['project_path'],
                    sess_data['chat_id']
                )
                session.status = sess_data.get('status', 'running')
                session.created_at = sess_data.get('created_at', datetime.now().isoformat())
                session.last_active = sess_data.get('last_active', datetime.now().isoformat())
                session.last_message = sess_data.get('last_message')
                session.pending_reply = sess_data.get('pending_reply', False)
                self.sessions[sid] = session
        except Exception as e:
            # If file is corrupted or empty, start fresh
            pass

    def _save_to_file(self):
        """Save sessions to shared file"""
        try:
            # Prepare data
            data = {sid: sess.to_dict() for sid, sess in self.sessions.items()}

            # Write with exclusive lock
            with open(self.storage_file, 'w') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock for writing
                json.dump(data, f, indent=2)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            # Log error but don't crash
            import logging
            logging.error(f"Failed to save sessions to file: {e}")

    def register(self, session_id: str, project_path: str, chat_id: str) -> Session:
        """Register a new session"""
        # Reload to get latest state
        self._load_from_file()

        session = Session(session_id, project_path, chat_id)
        self.sessions[session_id] = session

        # Save to file
        self._save_to_file()

        return session

    def get(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        # Reload to get latest state
        self._load_from_file()
        return self.sessions.get(session_id)

    def exists(self, session_id: str) -> bool:
        """Check if session exists"""
        # Reload to get latest state
        self._load_from_file()
        return session_id in self.sessions

    def list_all(self) -> Dict[str, Session]:
        """List all sessions"""
        # Reload to get latest state
        self._load_from_file()
        return self.sessions

    def list_waiting(self) -> Dict[str, Session]:
        """List sessions waiting for reply"""
        # Reload to get latest state
        self._load_from_file()
        return {
            sid: sess for sid, sess in self.sessions.items()
            if sess.pending_reply
        }

    def cleanup_idle(self, max_idle_seconds: int = 86400):
        """Clean up idle sessions (default 24 hours)"""
        # Reload to get latest state
        self._load_from_file()

        now = time.time()
        to_remove = []

        for sid, session in self.sessions.items():
            last_active = datetime.fromisoformat(session.last_active)
            idle_seconds = now - last_active.timestamp()
            if idle_seconds > max_idle_seconds:
                to_remove.append(sid)

        for sid in to_remove:
            del self.sessions[sid]

        # Save changes
        if to_remove:
            self._save_to_file()

        return to_remove

    def update_session(self, session: Session):
        """Update session state and save to file"""
        self.sessions[session.session_id] = session
        self._save_to_file()


# Global registry instance
registry = SessionRegistry()

