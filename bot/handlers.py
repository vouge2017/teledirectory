"""
TeleDirectory Phase 0 — Telegram bot handlers.
Auto-monitor channels + search + watchlist.
"""

import html
import re
from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import db
from config import (
    OPERATOR_IDS,
    MAX_SEARCH_RESULTS,
    MAX_WATCHLIST_PER_USER,
    TELEGRAM_LINK_BASE,
)


# ── Helpers ───────────────────────────────────────────────

def _is_operator(user_id: int) -> bool:
    return user_id in OPERATOR_IDS


def _deep_link(channel: str, msg_id: int) -> str:
    return f"{TELEGRAM_LINK_BASE}/{channel}/{msg_id}"


def _extract_price(text: str) -> str:
    """Pull a price from messy Ethiopian commerce text."""
    if not text:
        return ""
    patterns = [
        r'[Pp]rice[:\s-]*(\d[\d,\.]*)\s*(birr|etb|br|ብር|\$)?',
        r'(\d[\d,\.]*)\s*(birr|etb|br|ብር)',
        r'(\d[\d,\.]*)\s*(?:birr|etb|br)',
        r'ETB\s*(\d[\d,\.]*)',
        r'(\d{2,3},?\d{3})',  # 32,000 or 70000
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(0).strip()
    return ""


def _extract_phone(text: str) -> str:
    """Pull Ethiopian phone numbers from text."""
    if not text:
        return ""
    m = re.findall(r'(?:\+251|0)[97]\d{8}', text)
    return m[0] if m else ""


def _extract_telegram_user(text: str) -> str:
    """Pull @username mentions from text."""
    if not text:
        return ""
    m = re.findall(r'@(\w{4,})', text)
    # Filter out channel names (usually have underscores and long names)
    return f"@{m[0]}" if m else ""


def _extract_title(text: str) -> str:
    """Get a clean title from the first meaningful line."""
    if not text:
        return "Untitled"
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    for line in lines[:3]:
        # Skip lines that are just emojis or numbers
        clean = re.sub(r'[^\w\s]', '', line).strip()
        if len(clean) > 3:
            return line[:100]
    return lines[0][:100] if lines else "Untitled"


def _listing_card(listing: dict, show_id: bool = False) -> str:
    lines = []
    if show_id:
        lines.append(f"🆔 #{listing['id']}")
    lines.append(f"📱 <b>{html.escape(listing['title'])}</b>")
    if listing.get("price"):
        lines.append(f"💰 {html.escape(listing['price'])}")
    if listing.get("phone"):
        lines.append(f"📞 {html.escape(listing['phone'])}")
    if listing.get("username_mention"):
        lines.append(f"💬 {html.escape(listing['username_mention'])}")
    lines.append(f"📣 @{html.escape(listing['channel_username'])}")
    return "\n".join(lines)


def _listing_keyboard(listing: dict) -> InlineKeyboardMarkup:
    url = _deep_link(listing["channel_username"], listing["message_id"])
    buttons = [[InlineKeyboardButton("🔗 View Original Post", url=url)]]
    if listing.get("username_mention"):
        contact = listing["username_mention"].lstrip("@")
        buttons.append([InlineKeyboardButton("💬 Message Seller", url=f"https://t.me/{contact}")])
    elif listing.get("phone"):
        buttons.append([InlineKeyboardButton("📞 Call Seller", url=f"tel:{listing['phone']}")])
    return InlineKeyboardMarkup(buttons)


# ── /start ────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_op = _is_operator(update.effective_user.id)

    if is_op:
        welcome = (
            "📱 <b>TeleDirectory — Operator Mode</b>\n\n"
            "The bot <b>automatically monitors</b> channels you add.\n\n"
            "<b>Setup:</b>\n"
            "1. Add this bot as <b>admin</b> to your channel\n"
            "2. Send /monitor @channel_username here\n"
            "3. Done — every new post is auto-indexed\n\n"
            "<b>Commands:</b>\n"
            "/monitor @channel — start watching a channel\n"
            "/unmonitor @channel — stop watching\n"
            "/channels — see monitored channels\n"
            "/list — see all active listings\n"
            "/sold &lt;id&gt; — mark as sold\n"
            "/remove &lt;id&gt; — delete a listing\n"
            "/stats — counters\n\n"
            "<b>Buyers:</b> just type a word to search (e.g. <i>iphone</i>)"
        )
    else:
        welcome = (
            "📱 <b>TeleDirectory</b>\n\n"
            "Find fresh electronics listings in Addis Ababa.\n\n"
            "🔍 Just type what you're looking for\n"
            "   e.g. <i>iphone</i>, <i>samsung</i>, <i>laptop</i>\n\n"
            "🔔 /watch keyword — get alerts when new matches arrive\n"
            "📋 /mywatches — see your watches\n"
        )

    await update.message.reply_text(welcome, parse_mode=ParseMode.HTML)


# ── /search ───────────────────────────────────────────────

async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /search <keyword>\nOr just type a keyword directly.")
        return

    query = " ".join(context.args)
    results = db.search_listings(query, limit=MAX_SEARCH_RESULTS)
    db.log_search(update.effective_user.id, query, len(results))

    if not results:
        await update.message.reply_text(f'No listings found for "{query}".')
        return

    await update.message.reply_text(
        f'🔍 <b>{len(results)} result(s) for "{html.escape(query)}"</b>',
        parse_mode=ParseMode.HTML,
    )
    for listing in results:
        await update.message.reply_text(
            _listing_card(listing),
            parse_mode=ParseMode.HTML,
            reply_markup=_listing_keyboard(listing),
        )


# ── /watch / /unwatch / /mywatches ────────────────────────

async def cmd_watch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Usage: /watch <keyword>\n"
            "I'll DM you when a matching listing appears.\n"
            "Example: /watch iphone 15"
        )
        return

    user_id = update.effective_user.id
    query = " ".join(context.args)

    current = db.get_user_watches(user_id)
    if len(current) >= MAX_WATCHLIST_PER_USER:
        await update.message.reply_text(
            f"Watchlist full ({MAX_WATCHLIST_PER_USER} max). Remove one with /unwatch."
        )
        return

    if db.add_watch(user_id, query):
        await update.message.reply_text(
            f'🔔 Watching "<b>{html.escape(query)}</b>". '
            f"You'll get a DM when something matches.",
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.message.reply_text(
            f'Already watching "<b>{html.escape(query)}</b>".',
            parse_mode=ParseMode.HTML,
        )


async def cmd_unwatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /unwatch <keyword>")
        return

    query = " ".join(context.args)
    if db.remove_watch(update.effective_user.id, query):
        await update.message.reply_text(f'Removed watch for "{query}".')
    else:
        await update.message.reply_text(f'You weren\'t watching "{query}".')


async def cmd_mywatches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    watches = db.get_user_watches(update.effective_user.id)
    if not watches:
        await update.message.reply_text("No active watches. Use /watch <keyword> to set one.")
        return

    lines = ["🔔 <b>Your watches:</b>\n"]
    for w in watches:
        lines.append(f"  • {html.escape(w)}")
    lines.append("\n/unwatch <keyword> to remove one.")
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


# ── Operator: /monitor / /unmonitor / /channels ───────────

async def cmd_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_operator(update.effective_user.id):
        await update.message.reply_text("⛔ Operator-only command.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /monitor @channel_username\n\n"
            "Steps:\n"
            "1. Add this bot as admin to the channel\n"
            "2. Send /monitor @channel_username here\n\n"
            "The bot will auto-index every new post."
        )
        return

    channel = context.args[0].lstrip("@")
    existing = db.get_channel(channel)

    if existing and existing["is_active"]:
        await update.message.reply_text(f"Already monitoring @{channel}.")
        return

    db.add_channel(channel, added_by=update.effective_user.id)
    await update.message.reply_text(
        f"✅ Now monitoring <b>@{html.escape(channel)}</b>\n\n"
        f"⚠️ Make sure this bot is an <b>admin</b> in the channel!\n"
        f"New posts will be auto-indexed.",
        parse_mode=ParseMode.HTML,
    )


async def cmd_unmonitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_operator(update.effective_user.id):
        await update.message.reply_text("⛔ Operator-only command.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /unmonitor @channel")
        return

    channel = context.args[0].lstrip("@")
    if db.remove_channel(channel):
        await update.message.reply_text(f"Stopped monitoring @{channel}.")
    else:
        await update.message.reply_text(f"@{channel} wasn't being monitored.")


async def cmd_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_operator(update.effective_user.id):
        await update.message.reply_text("⛔ Operator-only command.")
        return

    channels = db.get_channels()
    if not channels:
        await update.message.reply_text(
            "No channels being monitored.\n"
            "Use /monitor @channel to add one."
        )
        return

    lines = [f"📡 <b>{len(channels)} monitored channel(s):</b>\n"]
    for ch in channels:
        lines.append(
            f"  @{html.escape(ch['channel_username'])} — "
            f"{ch['post_count']} posts"
            f"{'  ⚠️ bot not admin' if ch['post_count'] == 0 else ''}"
        )
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


# ── Channel post handler (auto-index) ─────────────────────

async def channel_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-index new posts from monitored channels.
    This fires when the bot is an admin in a channel and a new post appears."""
    post = update.channel_post
    if not post:
        return

    # Get channel username
    chat = post.chat
    channel_username = (chat.username or "").lower()

    if not channel_username:
        return

    # Check if we're monitoring this channel
    if not db.get_channel(channel_username):
        return

    # Skip if already indexed
    if db.listing_exists(channel_username, post.message_id):
        return

    # Extract data from the post
    text = post.text or post.caption or ""
    title = _extract_title(text)
    price = _extract_price(text)
    phone = _extract_phone(text)
    tg_user = _extract_telegram_user(text)

    # Get image URL if present
    image_url = ""
    if post.photo:
        # Get the largest photo
        photo = post.photo[-1]
        image_url = photo.file_id  # We'll use file_id for now

    # Store the listing
    try:
        listing_id = db.add_listing(
            channel_username=channel_username,
            message_id=post.message_id,
            title=title,
            price=price,
            description=text,
            image_url=image_url,
            phone=phone,
            username_mention=tg_user,
        )
    except Exception:
        return  # Duplicate or error, skip silently

    # Update channel post count
    db.update_channel_post_count(channel_username)

    # Notify matching watchers
    watcher_ids = db.get_matching_watchers(title, text)
    listing = db.get_listing(listing_id)

    for wid in watcher_ids:
        try:
            await context.bot.send_message(
                chat_id=wid,
                text=(
                    f"🔔 <b>New listing matches your watch!</b>\n\n"
                    f"{_listing_card(listing)}\n"
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=_listing_keyboard(listing),
            )
        except Exception:
            pass


# ── Operator: /list / /remove / /sold / /stats ───────────

async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_operator(update.effective_user.id):
        await update.message.reply_text("⛔ Operator-only command.")
        return

    listings = db.list_all("active", limit=30)
    if not listings:
        await update.message.reply_text("No active listings.")
        return

    lines = [f"📋 <b>{len(listings)} active listing(s):</b>\n"]
    for l in listings:
        clicks = db.get_clicks_for_listing(l["id"])
        lines.append(
            f"#{l['id']} — {html.escape(l['title'][:40])}"
            f"{(' | ' + html.escape(l['price'])) if l['price'] else ''}"
            f" | @{html.escape(l['channel_username'])}"
            f" | {clicks} click(s)"
        )
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def cmd_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_operator(update.effective_user.id):
        await update.message.reply_text("⛔ Operator-only command.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /remove <listing_id>")
        return

    try:
        lid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID must be a number.")
        return

    if db.remove_listing(lid):
        await update.message.reply_text(f"🗑 Removed listing #{lid}.")
    else:
        await update.message.reply_text(f"Listing #{lid} not found.")


async def cmd_sold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_operator(update.effective_user.id):
        await update.message.reply_text("⛔ Operator-only command.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /sold <listing_id>")
        return

    try:
        lid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID must be a number.")
        return

    if db.mark_sold(lid):
        await update.message.reply_text(f"✅ Marked #{lid} as sold.")
    else:
        await update.message.reply_text(f"Listing #{lid} not found.")


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_operator(update.effective_user.id):
        await update.message.reply_text("⛔ Operator-only command.")
        return

    s = db.get_stats()
    await update.message.reply_text(
        f"📊 <b>Stats</b>\n\n"
        f"📡 Monitored channels: {s['channels']}\n"
        f"📦 Active listings: {s['active']}\n"
        f"🏷 Total (incl. sold/removed): {s['total_listings']}\n"
        f"✅ Sold: {s['sold']}\n"
        f"🔔 Active watches: {s['watches']}\n"
        f"🔍 Total searches: {s['searches']}\n"
        f"🔗 Total deep-link clicks: {s['clicks']}",
        parse_mode=ParseMode.HTML,
    )


# ── Inline query ──────────────────────────────────────────

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()
    if not query or len(query) < 2:
        return

    results = db.search_listings(query, limit=MAX_SEARCH_RESULTS)
    db.log_search(update.inline_query.from_user.id, query, len(results))

    articles = []
    for listing in results:
        url = _deep_link(listing["channel_username"], listing["message_id"])
        card_text = _listing_card(listing)

        articles.append(
            InlineQueryResultArticle(
                id=str(listing["id"]),
                title=f"📱 {listing['title']}",
                description=f"{listing['price'] or ''} — @{listing['channel_username']}",
                input_message_content=InputTextMessageContent(
                    message_text=f"{card_text}\n\n🔗 <a href=\"{url}\">View Original Post</a>",
                    parse_mode=ParseMode.HTML,
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 View Original Post", url=url)],
                ]),
            )
        )

    await update.inline_query.answer(
        articles,
        cache_time=300,
        switch_pm_text="Search TeleDirectory" if not articles else None,
        switch_pm_parameter="start",
    )


# ── Callback query (click tracking) ──────────────────────

async def callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data or ""

    if data.startswith("click:"):
        try:
            lid = int(data.split(":")[1])
            db.log_click(query.from_user.id, lid)
            await query.answer("Opening original post…")
        except (ValueError, IndexError):
            await query.answer()
    else:
        await query.answer()


# ── Plain text search (type anything → search) ───────────

async def plain_text_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """If someone types text (not a command), search for it."""
    text = update.message.text.strip()
    if not text or len(text) < 2:
        return

    results = db.search_listings(text, limit=MAX_SEARCH_RESULTS)
    db.log_search(update.effective_user.id, text, len(results))

    if not results:
        await update.message.reply_text(
            f'No results for "{html.escape(text)}".\n'
            f'Try a different keyword.',
            parse_mode=ParseMode.HTML,
        )
        return

    await update.message.reply_text(
        f'🔍 <b>{len(results)} result(s) for "{html.escape(text)}"</b>',
        parse_mode=ParseMode.HTML,
    )
    for listing in results:
        await update.message.reply_text(
            _listing_card(listing),
            parse_mode=ParseMode.HTML,
            reply_markup=_listing_keyboard(listing),
        )
