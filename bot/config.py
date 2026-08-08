"""
TeleDirectory Phase 0 — Configuration
All settings in one place. No env-var spelunking.
"""

import os

# ── Telegram ──────────────────────────────────────────────
BOT_TOKEN = os.environ.get("TELEDIRECTORY_BOT_TOKEN", "")

# Telegram user IDs allowed to run operator commands (/add, /remove, /mark_sold)
# Comma-separated in env, e.g. "123456,789012"
_raw_ops = os.environ.get("TELEDIRECTORY_OPERATOR_IDS", "")
OPERATOR_IDS: set[int] = set()
for _s in _raw_ops.split(","):
    _s = _s.strip()
    if _s.isdigit():
        OPERATOR_IDS.add(int(_s))

# ── Database ──────────────────────────────────────────────
DB_PATH = os.environ.get("TELEDIRECTORY_DB", "teledirectory.db")

# ── Limits ────────────────────────────────────────────────
MAX_SEARCH_RESULTS = 10        # per /search or inline query
MAX_WATCHLIST_PER_USER = 20    # cap per buyer
LISTING_MAX_AGE_DAYS = 30      # auto-hide listings older than this
INLINE_CACHE_TIME = 300        # seconds — Telegram caches inline results

# ── Deep link base ────────────────────────────────────────
# For t.me links the bot builds automatically; no config needed.
# But if channels have custom domain, set here:
TELEGRAM_LINK_BASE = "https://t.me"
