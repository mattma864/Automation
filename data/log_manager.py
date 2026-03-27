"""
data/log_manager.py
--------------------
Manages the persistent send log stored as JSON in logs/send_log.json.
"""

import json
import os
from datetime import datetime

from config.settings import LOG_PATH


def _ensure_log_dir():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


def load_log() -> list:
    """Load existing log entries. Returns [] if file does not exist."""
    _ensure_log_dir()
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r") as f:
        return json.load(f)


def save_log(entries: list) -> None:
    """Persist the full list of log entries to disk."""
    _ensure_log_dir()
    with open(LOG_PATH, "w") as f:
        json.dump(entries, f, indent=2)


def append_entry(entries: list, to: str, subject: str,
                 job_count: int, status: str) -> list:
    """Append a new log entry and return the updated list."""
    entries.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "to":        to,
        "subject":   subject,
        "jobs":      job_count,
        "status":    status,
    })
    save_log(entries)
    return entries


def clear_log() -> list:
    """Wipe all log entries and return empty list."""
    save_log([])
    return []
