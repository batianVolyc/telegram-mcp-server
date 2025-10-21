"""Message queue management"""
import os
import json
import fcntl
from typing import Dict, List
from collections import defaultdict

# Shared message queue storage file
QUEUE_STORAGE_FILE = os.path.expanduser("~/.claude/telegram-mcp-queue.json")


class MessageQueue:
    """Per-session message queue with shared file storage"""

    def __init__(self):
        self.queues: Dict[str, List[str]] = defaultdict(list)
        self.storage_file = QUEUE_STORAGE_FILE

        # Ensure storage directory exists
        storage_dir = os.path.dirname(self.storage_file)
        os.makedirs(storage_dir, exist_ok=True)

        # Load existing queues from file
        self._load_from_file()

    def _load_from_file(self):
        """Load queues from shared file"""
        if not os.path.exists(self.storage_file):
            return

        try:
            with open(self.storage_file, 'r') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # Shared lock for reading
                data = json.load(f)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # Reconstruct queues
            self.queues = defaultdict(list, data)
        except Exception:
            # If file is corrupted or empty, start fresh
            pass

    def _save_to_file(self):
        """Save queues to shared file"""
        try:
            # Prepare data
            data = dict(self.queues)

            # Write with exclusive lock
            with open(self.storage_file, 'w') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock for writing
                json.dump(data, f, indent=2)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            # Log error but don't crash
            import logging
            logging.error(f"Failed to save message queue to file: {e}")

    def push(self, session_id: str, message: str):
        """Add message to session queue"""
        # Reload to get latest state
        self._load_from_file()

        self.queues[session_id].append(message)

        # Save to file
        self._save_to_file()

    def pop(self, session_id: str) -> str:
        """Get and remove first message from queue"""
        # Reload to get latest state
        self._load_from_file()

        if session_id in self.queues and self.queues[session_id]:
            message = self.queues[session_id].pop(0)
            # Save to file
            self._save_to_file()
            return message
        return None

    def peek(self, session_id: str) -> str:
        """Get first message without removing"""
        # Reload to get latest state
        self._load_from_file()

        if session_id in self.queues and self.queues[session_id]:
            return self.queues[session_id][0]
        return None

    def has_messages(self, session_id: str) -> bool:
        """Check if session has pending messages"""
        # Reload to get latest state
        self._load_from_file()

        return session_id in self.queues and len(self.queues[session_id]) > 0

    def clear(self, session_id: str):
        """Clear all messages for a session"""
        # Reload to get latest state
        self._load_from_file()

        if session_id in self.queues:
            self.queues[session_id].clear()
            # Save to file
            self._save_to_file()


# Global queue instance
message_queue = MessageQueue()
