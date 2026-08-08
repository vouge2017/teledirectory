"""
TeleDirectory Phase 0 — SQLite database layer.
Single file, zero dependencies beyond stdlib.
Schema auto-creates on first access.
"""

import sqlite3
import time
from contextlib import contextmanager
from config import DB_PATH, LISTING_MAX_AGE_DAYS

# ── Schema ────────────────────────────────────────────────

_SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_username TEXT NOT NULL,          -- without @, e.g. "BoleElectronics"
    message_id      INTEGER NOT NULL,        -- original post message_id
    title           TEXT NOT NULL,            -- first line or operator-supplied title
    price           TEXT,                     -- free-text, e.g. "85,000 Birr"
    description     TEXT,                     -- full post text (optional)
    image_url       TEXT,                     -- URL or file_id of photo
    category        TEXT DEFAULT '',          -- optional tag: "phones", "laptops", etc.
    status          TEXT DEFAULT 'active',    -- active | sold | removed
    added_by        INTEGER,                 -- operator telegram user id
    created_at      REAL NOT NULL,           -- unix timestamp
    updated_at      REAL NOT NULL,
    UNIQUE(channel_username, message_id)
);

CREATE TABLE IF NOT EXISTS watchlist (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,         -- buyer telegram user id
    query           TEXT NOT NULL,             -- search term, e.g. "iphone 15"
    created_at      REAL NOT NULL,
    UNIQUE(user_id, query)                    -- one watch per term per user
);

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
CREATE INDEX IF NOT EXISTS idx_watchlist_query ON watchlist(query);
"""

def init_db(db_path: str = DB_PATH) -> None:
    """Create tables if they don't exist."""
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


# ── Listings CRUD ─────────────────────────────────────────

def add_listing(
    channel_username: str,
    message_id: int,
    title: str,
    price: str = "",
    description: str = "",
    image_url: str = "",
    category: str = "",
    added_by: int = 0,
) -> int:
    """Insert a new listing. Returns listing id. Raises on duplicate."""
    now = time.time()
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO listings
               (channel_username, message_id, title, price, description,
                image_url, category, added_by, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (channel_username, message_id, title, price, description,
             image_url, category, added_by, now, now),
        )
        return cur.lastrowid


def get_listing(listing_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM listings WHERE id = ?", (listing_id,)
        ).fetchone()
        return dict(row) if row else None


def search_listings(query: str, limit: int = 10) -> list[dict]:
    """Simple LIKE search across title + description + category.
    Good enough for Phase 0 with < 1000 listings."""
    cutoff = time.time() - (LISTING_MAX_AGE_DAYS * 86400)
    pattern = f"%{query}%"
    with _connect() as conn:
        rows = conn.execute(
            """SELECT * FROM listings
               WHERE status = 'active'
                 AND created_at > ?
                 AND (title LIKE ? OR description LIKE ? OR category LIKE ?)
               ORDER BY created_at DESC
               LIMIT ?""",
            (cutoff, pattern, pattern, pattern, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def list_all(status: str = "active", limit: int = 50) -> list[dict]:
    cutoff = time.time() - (LISTING_MAX_AGE_DAYS * 86400)
    with _connect() as conn:
        rows = conn.execute(
            """SELECT * FROM listings
               WHERE status = ? AND created_at > ?
               ORDER BY created_at DESC LIMIT ?""",
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


# ── Watchlist ─────────────────────────────────────────────

def add_watch(user_id: int, query: str) -> bool:
    """Add a watch. Returns False if already watching."""
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


def get_matching_watchers(title: str, description: str = "", category: str = "") -> list[int]:
    """Find all user_ids whose watch queries match a new listing.
    Returns deduplicated list of user_ids to notify."""
    text = f"{title} {description} {category}".lower()
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
        active = conn.execute(
            "SELECT COUNT(*) c FROM listings WHERE status='active'"
        ).fetchone()["c"]
        sold = conn.execute(
            "SELECT COUNT(*) c FROM listings WHERE status='sold'"
        ).fetchone()["c"]
        watches = conn.execute("SELECT COUNT(*) c FROM watchlist").fetchone()["c"]
        searches = conn.execute("SELECT COUNT(*) c FROM search_log").fetchone()["c"]
        clicks = conn.execute("SELECT COUNT(*) c FROM click_log").fetchone()["c"]
        return {
            "total_listings": total,
            "active": active,
            "sold": sold,
            "watches": watches,
            "searches": searches,
            "clicks": clicks,
        }


def get_clicks_for_listing(listing_id: int) -> int:
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) c FROM click_log WHERE listing_id = ?",
            (listing_id,),
        ).fetchone()
        return row["c"]
