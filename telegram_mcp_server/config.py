"""Configuration management"""
import os

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Session Configuration
TELEGRAM_SESSION_ID = os.getenv("TELEGRAM_SESSION")  # User-defined session ID
TELEGRAM_MAX_WAIT = int(os.getenv("TELEGRAM_MAX_WAIT", "604800"))  # Default 7 days (1 week)

# Polling intervals (in seconds) for different time periods
POLL_INTERVALS = os.getenv("TELEGRAM_POLL_INTERVAL", "30,60,120").split(",")
POLL_INTERVALS = [int(x) for x in POLL_INTERVALS]

# Time thresholds for polling intervals (in seconds)
POLL_THRESHOLDS = [600, 3600]  # 10 minutes, 1 hour

def validate_config():
    """Validate required configuration"""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
    if not TELEGRAM_CHAT_ID:
        raise ValueError("TELEGRAM_CHAT_ID environment variable is required")
    return True
