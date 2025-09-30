"""Simple JSON-lines audit logging utility.

Writes append-only structured events for security-relevant actions.

Schema (per line JSON):
{
  "ts": ISO8601 string,
  "event": short event name (e.g. group.created, expense.added),
  "actor_id": user id or null,
  "actor_ip": best-effort remote IP (optional),
  "details": arbitrary dict (must be JSON-serializable)
}

Configuration:
- AUDIT_LOG_FILE from settings (default: audit.log in backend root)

This is intentionally lightweight; rotation / central shipping should be
handled externally (e.g. logrotate, container stdout collection).
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from typing import Any, Optional

from src.settings import get_settings

_lock = threading.Lock()
_settings = get_settings()
_AUDIT_PATH = getattr(_settings, "AUDIT_LOG_FILE", "audit.log")


def audit(event: str, actor_id: Optional[str], details: dict[str, Any], actor_ip: Optional[str] = None) -> None:
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "actor_id": actor_id,
        "actor_ip": actor_ip,
        "details": details,
    }
    line = json.dumps(record, ensure_ascii=False)
    # Ensure directory exists
    os.makedirs(os.path.dirname(_AUDIT_PATH) or ".", exist_ok=True)
    with _lock:
        with open(_AUDIT_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")

__all__ = ["audit"]
