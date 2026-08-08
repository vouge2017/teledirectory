"""
TeleDirectory Phase 0 — SQLite database layer.
Auto-monitored channels + listings + watchlist.
"""

import sqlite3
import time
from contextlib import contextmanager
from config import DB_PATH, LISTING_MAX_AGE_DAYS

_SCHEMA = """
-- Channels the bot is monitoring (bot must be admin)
CREATE TABLE IF NOT EXISTS channels (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_username TEXT NOT NULL UNIQUE,     -- without @
    channel_id      INTEGER,                  -- Telegram channel ID (if known)
    title           TEXT DEFAULT '',
    added_by        INTEGER,
    is_active       INTEGER DEFAULT 1,
    last_post_at    REAL,
    post_count      INTEGER DEFAULT 0,
    created_at      REAL NOT NULL
);

-- Listings auto-indexed from channels
CREATE TABLE IF NOT EXISTS listings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_username TEXT NOT NULL,
    message_id      INTEGER NOT NULL,
    title           TEXT NOT NULL,
    price           TEXT DEFAULT '',
    description     TEXT DEFAULT '',
    image_url       TEXT DEFAULT '',
    category        TEXT DEFAULT '',
    phone           TEXT DEFAULT '',
    username_mention TEXT DEFAULT '',
    status          TEXT DEFAULT 'active',
    created_at      REAL NOT NULL,
    updated_at      REAL NOT NULL,
    UNIQUE(channel_username, message_id)
);

-- Buyer watchlist
CREATE TABLE IF NOT EXISTS watchlist (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    query           TEXT NOT NULL,
    created_at      REAL NOT NULL,
    UNIQUE(user_id, query)
);

-- Logs
CREATE TABLE IF NOT EXISTS search_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    query           TEXT NOT NULL,
    results_count   INTEGER DEFAULT 0,
    created_at      REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS click_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    listing_id      INTEGER NOT NULL,
    created_at      REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_listings_status ON listings(status);
CREATE INDEX IF NOT EXISTS idx_listings_created ON listings(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_listings_channel ON listings(channel_username);
CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlist(user_id);
CREATE INDEX IF NOT EXISTS idx_channels_active ON channels(is_active);
"""


def init_db(db_path: str = DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.executescript(_SCHEMA)


@contextmanager
def _connect(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ── Channels ──────────────────────────────────────────────

def add_channel(username: str, title: str = "", channel_id: int = 0, added_by: int = 0) -> int:
    now = time.time()
    with _connect() as conn:
        cur = conn.execute(
            """INSERT OR IGNORE INTO channels
               (channel_username, channel_id, title, added_by, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (username.lower().lstrip("@"), channel_id, title, added_by, now),
        )
        return cur.lastrowid


def get_channels(active_only: bool = True) -> list[dict]:
    with _connect() as conn:
        q = "SELECT * FROM channels"
        if active_only:
            q += " WHERE is_active = 1"
        q += " ORDER BY created_at DESC"
        return [dict(r) for r in conn.execute(q).fetchall()]


def get_channel(username: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM channels WHERE channel_username = ?",
            (username.lower().lstrip("@"),),
        ).fetchone()
        return dict(row) if row else None


def remove_channel(username: str) -> bool:
    with _connect() as conn:
        cur = conn.execute(
            "UPDATE channels SET is_active = 0 WHERE channel_username = ?",
            (username.lower().lstrip("@"),),
        )
        return cur.rowcount > 0


def update_channel_post_count(username: str) -> None:
    with _connect() as conn:
        conn.execute(
            """UPDATE channels SET
               post_count = (SELECT COUNT(*) FROM listings WHERE channel_username = ?),
               last_post_at = ?
               WHERE channel_username = ?""",
            (username.lower().lstrip("@"), time.time(), username.lower().lstrip("@")),
        )


# ── Listings ──────────────────────────────────────────────

def add_listing(
    channel_username: str,
    message_id: int,
    title: str,
    price: str = "",
    description: str = "",
    image_url: str = "",
    category: str = "",
    phone: str = "",
    username_mention: str = "",
) -> int:
    now = time.time()
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO listings
               (channel_username, message_id, title, price, description,
                image_url, category, phone, username_mention, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (channel_username.lower().lstrip("@"), message_id, title, price,
             description, image_url, category, phone, username_mention, now, now),
        )
        return cur.lastrowid


def get_listing(listing_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
        return dict(row) if row else None


def search_listings(query: str, limit: int = 10) -> list[dict]:
    cutoff = time.time() - (LISTING_MAX_AGE_DAYS * 86400)
    pattern = f"%{query}%"
    with _connect() as conn:
        rows = conn.execute(
            """SELECT * FROM listings
               WHERE status = 'active'
                 AND created_at > ?
                 AND (title LIKE ? OR description LIKE ? OR category LIKE ? OR channel_username LIKE ?)
               ORDER BY created_at DESC
               LIMIT ?""",
            (cutoff, pattern, pattern, pattern, pattern, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def list_all(status: str = "active", limit: int = 50) -> list[dict]:
    cutoff = time.time() - (LISTING_MAX_AGE_DAYS * 86400)
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM listings WHERE status = ? AND created_at > ? ORDER BY created_at DESC LIMIT ?",
            (status, cutoff, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def remove_listing(listing_id: int) -> bool:
    with _connect() as conn:
        cur = conn.execute(
            "UPDATE listings SET status = 'removed', updated_at = ? WHERE id = ?",
            (time.time(), listing_id),
        )
        return cur.rowcount > 0


def mark_sold(listing_id: int) -> bool:
    with _connect() as conn:
        cur = conn.execute(
            "UPDATE listings SET status = 'sold', updated_at = ? WHERE id = ?",
            (time.time(), listing_id),
        )
        return cur.rowcount > 0


def listing_exists(channel_username: str, message_id: int) -> bool:
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM listings WHERE channel_username = ? AND message_id = ?",
            (channel_username.lower().lstrip("@"), message_id),
        ).fetchone()
        return row is not None


# ── Watchlist ─────────────────────────────────────────────

def add_watch(user_id: int, query: str) -> bool:
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO watchlist (user_id, query, created_at) VALUES (?, ?, ?)",
                (user_id, query.lower().strip(), time.time()),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def remove_watch(user_id: int, query: str) -> bool:
    with _connect() as conn:
        cur = conn.execute(
            "DELETE FROM watchlist WHERE user_id = ? AND query = ?",
            (user_id, query.lower().strip()),
        )
        return cur.rowcount > 0


def get_user_watches(user_id: int) -> list[str]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT query FROM watchlist WHERE user_id = ? ORDER BY created_at",
            (user_id,),
        ).fetchall()
        return [r["query"] for r in rows]


def get_matching_watchers(title: str, description: str = "") -> list[int]:
    text = f"{title} {description}".lower()
    with _connect() as conn:
        rows = conn.execute("SELECT DISTINCT user_id, query FROM watchlist").fetchall()
        matched = set()
        for r in rows:
            if r["query"] in text:
                matched.add(r["user_id"])
        return list(matched)


# ── Logging ───────────────────────────────────────────────

def log_search(user_id: int, query: str, results_count: int) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO search_log (user_id, query, results_count, created_at) VALUES (?, ?, ?, ?)",
            (user_id, query, results_count, time.time()),
        )


def log_click(user_id: int, listing_id: int) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO click_log (user_id, listing_id, created_at) VALUES (?, ?, ?)",
            (user_id, listing_id, time.time()),
        )


# ── Stats ─────────────────────────────────────────────────

def get_stats() -> dict:
    with _connect() as conn:
        total = conn.execute("SELECT COUNT(*) c FROM listings").fetchone()["c"]
        active = conn.execute("SELECT COUNT(*) c FROM listings WHERE status='active'").fetchone()["c"]
        sold = conn.execute("SELECT COUNT(*) c FROM listings WHERE status='sold'").fetchone()["c"]
        watches = conn.execute("SELECT COUNT(*) c FROM watchlist").fetchone()["c"]
        searches = conn.execute("SELECT COUNT(*) c FROM search_log").fetchone()["c"]
        clicks = conn.execute("SELECT COUNT(*) c FROM click_log").fetchone()["c"]
        channels = conn.execute("SELECT COUNT(*) c FROM channels WHERE is_active=1").fetchone()["c"]
        return {
            "total_listings": total,
            "active": active,
            "sold": sold,
            "watches": watches,
            "searches": searches,
            "clicks": clicks,
            "channels": channels,
        }


def get_clicks_for_listing(listing_id: int) -> int:
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) c FROM click_log WHERE listing_id = ?", (listing_id,),
        ).fetchone()
        return row["c"]
