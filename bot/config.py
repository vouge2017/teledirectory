"""
TeleDirectory Phase 0 — Configuration
Supports .env file.
"""

import os
from pathlib import Path


def _load_env():
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip()
            if k and k not in os.environ:
                os.environ[k] = v


_load_env()

# ── Telegram ──────────────────────────────────────────────
BOT_TOKEN = os.environ.get("TELEDIRECTORY_BOT_TOKEN", "")

# Operator Telegram user IDs (comma-separated)
_raw_ops = os.environ.get("TELEDIRECTORY_OPERATOR_IDS", "")
OPERATOR_IDS: set[int] = set()
for _s in _raw_ops.split(","):
    _s = _s.strip()
    if _s.isdigit():
        OPERATOR_IDS.add(int(_s))

# ── Database ──────────────────────────────────────────────
DB_PATH = os.environ.get("TELEDIRECTORY_DB", "teledirectory.db")

# ── Limits ────────────────────────────────────────────────
MAX_SEARCH_RESULTS = 10
MAX_WATCHLIST_PER_USER = 20
LISTING_MAX_AGE_DAYS = 30

# ── Deep link ─────────────────────────────────────────────
TELEGRAM_LINK_BASE = "https://t.me"
