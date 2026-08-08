"""
TeleDirectory Phase 0 — Channel Monitor
Uses a Telegram user account to read public channels automatically.
No admin access needed.

First run: interactive login (verification code required).
After that: runs silently, indexing new posts.
"""

import asyncio
import logging
import os
import re
import time
from pathlib import Path

from telethon import TelegramClient, events
from telethon.tl.types import Message

# ── Config ────────────────────────────────────────────────

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

API_ID = int(os.environ.get("TELETHON_API_ID", "0"))
API_HASH = os.environ.get("TELETHON_API_HASH", "")
PHONE = os.environ.get("TELETHON_PHONE", "")
DB_PATH = os.environ.get("TELEDIRECTORY_DB", "teledirectory.db")
SESSION_PATH = str(Path(__file__).parent / "monitor_session")

# ── Logging ───────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("monitor")

# ── Database (same as bot.py uses) ────────────────────────

import sqlite3
from contextlib import contextmanager

@contextmanager
def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def get_monitored_channels() -> list[str]:
    """Get list of channel usernames to monitor."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT channel_username FROM channels WHERE is_active = 1"
        ).fetchall()
        return [r["channel_username"] for r in rows]


def listing_exists(channel: str, msg_id: int) -> bool:
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM listings WHERE channel_username = ? AND message_id = ?",
            (channel, msg_id),
        ).fetchone()
        return row is not None


def add_listing(channel: str, msg_id: int, title: str, price: str,
                description: str, image_url: str, phone: str, tg_user: str) -> int:
    now = time.time()
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO listings
               (channel_username, message_id, title, price, description,
                image_url, phone, username_mention, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (channel, msg_id, title, price, description, image_url, phone, tg_user, now, now),
        )
        return cur.lastrowid


def get_matching_watchers(title: str, description: str = "") -> list[int]:
    text = f"{title} {description}".lower()
    with _connect() as conn:
        rows = conn.execute("SELECT DISTINCT user_id, query FROM watchlist").fetchall()
        matched = set()
        for r in rows:
            if r["query"] in text:
                matched.add(r["user_id"])
        return list(matched)


def update_channel_post_count(channel: str) -> None:
    with _connect() as conn:
        conn.execute(
            """UPDATE channels SET
               post_count = (SELECT COUNT(*) FROM listings WHERE channel_username = ?),
               last_post_at = ?
               WHERE channel_username = ?""",
            (channel, time.time(), channel),
        )


# ── Extraction helpers ────────────────────────────────────

def extract_price(text: str) -> str:
    if not text:
        return ""
    patterns = [
        r'[Pp]rice[:\s-]*(\d[\d,\.]*)\s*(birr|etb|br|ብር|\$)?',
        r'(\d[\d,\.]*)\s*(birr|etb|br|ብር)',
        r'(\d[\d,\.]*)\s*(?:birr|etb|br)',
        r'ETB\s*(\d[\d,\.]*)',
        r'(\d{2,3},?\d{3})',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(0).strip()
    return ""


def extract_phone(text: str) -> str:
    if not text:
        return ""
    m = re.findall(r'(?:\+251|0)[97]\d{8}', text)
    return m[0] if m else ""


def extract_telegram_user(text: str) -> str:
    if not text:
        return ""
    m = re.findall(r'@(\w{4,})', text)
    return f"@{m[0]}" if m else ""


def extract_title(text: str) -> str:
    if not text:
        return "Untitled"
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    for line in lines[:3]:
        clean = re.sub(r'[^\w\s]', '', line).strip()
        if len(clean) > 3:
            return line[:100]
    return lines[0][:100] if lines else "Untitled"


# ── Main monitor ──────────────────────────────────────────

async def main():
    if not API_ID or not API_HASH:
        logger.error("Missing TELETHON_API_ID or TELETHON_API_HASH in .env")
        return

    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
    await client.start(phone=PHONE)
    logger.info(f"Logged in as user account.")

    # Get channels to monitor
    channels = get_monitored_channels()
    if not channels:
        logger.warning("No channels to monitor. Use /monitor @channel in the bot first.")
        logger.warning("Waiting for channels to appear in database...")
        # We'll poll for new channels periodically

    logger.info(f"Monitoring {len(channels)} channel(s): {channels}")

    # Track which channels we're watching
    watching: set[str] = set(channels)

    @client.on(events.NewMessage(chats=watching if watching else None))
    async def handler(event):
        """Auto-index new posts from monitored channels."""
        msg: Message = event.message
        chat = event.chat

        if not chat or not chat.username:
            return

        channel = chat.username.lower()

        # Double-check we're monitoring this channel
        if channel not in watching:
            return

        # Skip if already indexed
        if listing_exists(channel, msg.id):
            return

        # Extract data
        text = msg.text or ""
        title = extract_title(text)
        price = extract_price(text)
        phone = extract_phone(text)
        tg_user = extract_telegram_user(text)
        image_url = ""

        if msg.photo:
            # We can't easily get a URL from Telethon photos,
            # but we can note that there IS a photo
            image_url = f"photo:{msg.id}"

        # Store it
        try:
            lid = add_listing(
                channel=channel,
                msg_id=msg.id,
                title=title,
                price=price,
                description=text,
                image_url=image_url,
                phone=phone,
                tg_user=tg_user,
            )
            update_channel_post_count(channel)
            logger.info(f"✅ Indexed #{lid}: {title[:40]} | {price} | @{channel}/{msg.id}")
        except Exception as e:
            if "UNIQUE" in str(e):
                pass  # Already indexed
            else:
                logger.error(f"Error indexing @{channel}/{msg.id}: {e}")
            return

        # Notify watchers (we'd need to send via bot, but for now just log)
        watchers = get_matching_watchers(title, text)
        if watchers:
            logger.info(f"  → {len(watchers)} watchers would be notified")

    # Periodic channel refresh (in case operator adds new channels via bot)
    async def refresh_channels():
        while True:
            await asyncio.sleep(60)  # Check every minute
            new_channels = get_monitored_channels()
            for ch in new_channels:
                if ch not in watching:
                    watching.add(ch)
                    logger.info(f"📡 New channel detected: @{ch}")

            for ch in list(watching):
                if ch not in new_channels:
                    watching.discard(ch)
                    logger.info(f"📡 Channel removed: @{ch}")

    asyncio.create_task(refresh_channels())

    logger.info("Monitor running. Press Ctrl+C to stop.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
