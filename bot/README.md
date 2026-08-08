# TeleDirectory — Phase 0 Bot

Thin Telegram bot for operator-managed electronics listings in Addis Ababa.

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Set env vars
export TELEDIRECTORY_BOT_TOKEN="your-bot-token-from-botfather"
export TELEDIRECTORY_OPERATOR_IDS="your_telegram_id,another_operator_id"

# 3. Run
python bot.py
```

## Commands

### Buyer commands
| Command | What it does |
|---------|-------------|
| `/start` | Welcome message |
| `/search iphone 15` | Search listings by keyword |
| `/watch samsung galaxy` | Get DM alerts when matching listings are added |
| `/unwatch samsung galaxy` | Remove a watch |
| `/mywatches` | See your active watches |
| `@botname iphone` | Inline search from any chat |

### Operator commands
| Command | What it does |
|---------|-------------|
| `/add @channel 12345 iPhone 15 Pro 85000 Birr` | Add a listing manually |
| `/forward_add` | Forward a channel post → auto-extract & add |
| `/list` | Show all active listings |
| `/remove 42` | Hide a listing |
| `/sold 42` | Mark a listing as sold |
| `/stats` | View counters (listings, watches, searches, clicks) |

## How it works

1. **Operator** sees a good listing in a cooperating channel → forwards it to the bot (or uses `/add`).
2. **Buyer** searches `/search iphone` → sees result cards with a **"View Original Post"** button.
3. Buyer taps → lands on the original `t.me/channel/message_id` → contacts seller directly.
4. If a buyer has a **watch** set, they get a DM alert when a matching listing is added.

## Files

- `bot.py` — entry point
- `config.py` — all settings
- `db.py` — SQLite schema + CRUD
- `handlers.py` — all Telegram handlers

## Data

All data lives in `teledirectory.db` (SQLite). Single file. Back it up by copying it.

## What's NOT here (by design)

- No scraping automation
- No merchant self-onboarding
- No verification tiers
- No payments or promoted listings
- No frontend (Mini App)
- No PostgreSQL or Redis
