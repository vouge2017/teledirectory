"""
TeleDirectory Phase 0 — Telegram bot handlers.
All /commands, inline queries, and callback queries.
"""

import html
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
    """Build t.me/channel/msg_id link."""
    return f"{TELEGRAM_LINK_BASE}/{channel}/{msg_id}"


def _listing_card(listing: dict, show_id: bool = False) -> str:
    """Render a listing as a short text block (Telegram-safe, no markdown tables)."""
    lines = []
    if show_id:
        lines.append(f"🆔 #{listing['id']}")
    lines.append(f"📱 <b>{html.escape(listing['title'])}</b>")
    if listing["price"]:
        lines.append(f"💰 {html.escape(listing['price'])}")
    if listing["category"]:
        lines.append(f"🏷 {html.escape(listing['category'])}")
    lines.append(f"📣 @{html.escape(listing['channel_username'])}")
    return "\n".join(lines)


def _listing_keyboard(listing: dict) -> InlineKeyboardMarkup:
    """Inline keyboard with 'View Original Post' deep-link button."""
    url = _deep_link(listing["channel_username"], listing["message_id"])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 View Original Post", url=url)],
    ])


# ── /start ────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "📱 <b>TeleDirectory</b>\n\n"
        "Find fresh electronics listings in Addis Ababa.\n\n"
        "🔍 <b>Search:</b> /search <i>keyword</i>\n"
        "🔔 <b>Watch:</b> /watch <i>keyword</i>  — get alerts on new matches\n"
        "📋 <b>My watches:</b> /mywatches\n\n"
        "Or use inline: type <code>@botname iphone</code> in any chat.\n"
    )
    if _is_operator(update.effective_user.id):
        welcome += (
            "\n── Operator commands ──\n"
            "/add &lt;channel&gt; &lt;msg_id&gt; &lt;title&gt; [price]\n"
            "/list — show active listings\n"
            "/remove &lt;id&gt; — hide a listing\n"
            "/sold &lt;id&gt; — mark as sold\n"
            "/stats — counters\n"
        )
    await update.message.reply_text(welcome, parse_mode=ParseMode.HTML)


# ── /search ───────────────────────────────────────────────

async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /search <keyword>\nExample: /search iphone 15")
        return

    query = " ".join(context.args)
    results = db.search_listings(query, limit=MAX_SEARCH_RESULTS)
    db.log_search(update.effective_user.id, query, len(results))

    if not results:
        await update.message.reply_text(f'No listings found for "{query}".')
        return

    await update.message.reply_text(
        f'🔍 <b>{len(results)} result(s) for "{html.escape(query)}"</b>\n'
        f"Tap a listing to view the original post.",
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
            "I'll DM you when a matching listing is added.\n"
            "Example: /watch samsung galaxy"
        )
        return

    user_id = update.effective_user.id
    query = " ".join(context.args)

    # Check limit
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


# ── Operator: /add ────────────────────────────────────────

async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not _is_operator(uid):
        await update.message.reply_text("⛔ Operator-only command.")
        return

    # Expected: /add @channel 12345 Title here 85,000 Birr
    # or:     /add channel 12345 Title here 85,000 Birr
    if len(context.args) < 3:
        await update.message.reply_text(
            "Usage: /add <channel> <msg_id> <title> [price]\n"
            "Example: /add @BoleElectronics 12345 iPhone 15 Pro Max 85000 Birr\n\n"
            "Tip: You can also forward a post from a cooperating channel "
            "and I'll try to extract the info automatically."
        )
        return

    channel = context.args[0].lstrip("@")
    try:
        msg_id = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Message ID must be a number.")
        return

    # Title is everything between msg_id and the last arg (if it looks like a price)
    # Simple heuristic: if the last token has digits and a price word, treat as price
    remaining = context.args[2:]
    price = ""
    title_parts = list(remaining)

    # Check if last 1-2 tokens look like a price (digits + optional currency)
    if len(remaining) >= 2:
        last_two = " ".join(remaining[-2:])
        last_one = remaining[-1]
        if any(c.isdigit() for c in last_one) and len(last_one) < 15:
            # Could be price — but only if there's more than just a "title"
            if any(word.lower() in last_two.lower() for word in ["birr", "etb", "br", "price"]):
                price = last_two
                title_parts = remaining[:-2]
            elif len(remaining) >= 3 and any(c.isdigit() for c in last_one):
                price = last_one
                title_parts = remaining[:-1]

    title = " ".join(title_parts) or channel  # fallback to channel name

    try:
        listing_id = db.add_listing(
            channel_username=channel,
            message_id=msg_id,
            title=title,
            price=price,
            added_by=uid,
        )
    except Exception as e:
        if "UNIQUE" in str(e):
            await update.message.reply_text(
                f"Already added: @{channel}/{msg_id}"
            )
        else:
            await update.message.reply_text(f"Error: {e}")
        return

    # Notify matching watchers
    watcher_ids = db.get_matching_watchers(title, price)
    for wid in watcher_ids:
        try:
            await context.bot.send_message(
                chat_id=wid,
                text=(
                    f"🔔 <b>New listing matches your watch!</b>\n\n"
                    f"{_listing_card(db.get_listing(listing_id))}\n"
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=_listing_keyboard(db.get_listing(listing_id)),
            )
        except Exception:
            pass  # user may have blocked the bot

    await update.message.reply_text(
        f"✅ Added #{listing_id}: <b>{html.escape(title)}</b>\n"
        f"🔗 {_deep_link(channel, msg_id)}\n"
        f"Notified {len(watcher_ids)} watcher(s).",
        parse_mode=ParseMode.HTML,
    )


# ── Operator: /forward_add (handle forwarded posts) ──────

async def cmd_forward_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Use when operator forwards a channel post to the bot.
    Bot extracts info from the forwarded message."""
    uid = update.effective_user.id
    if not _is_operator(uid):
        await update.message.reply_text("⛔ Operator-only command.")
        return

    msg = update.message
    fwd = msg.forward_origin  # v20+ uses forward_origin

    if not fwd:
        await update.message.reply_text(
            "Forward a post from a cooperating channel, then reply /forward_add to it.\n"
            "Or use: /add <channel> <msg_id> <title> [price]"
        )
        return

    # Extract channel info from forward_origin
    channel_username = ""
    message_id = 0

    if hasattr(fwd, "chat") and fwd.chat:
        # Forwarded from a channel
        channel_username = fwd.chat.username or ""
        message_id = fwd.message_id if hasattr(fwd, "message_id") else 0
    elif hasattr(fwd, "sender_user_name"):
        # Forwarded from a user — not what we want
        await update.message.reply_text(
            "This looks like it was forwarded from a user, not a channel.\n"
            "Forward a post from a cooperating electronics channel."
        )
        return

    if not channel_username:
        await update.message.reply_text(
            "Could not extract channel username from this forward.\n"
            "Use /add manually: /add @channel 123 Title"
        )
        return

    # Try to extract title and price from the forwarded message text
    text = msg.text or msg.caption or ""
    lines = text.strip().split("\n")
    title = lines[0][:100] if lines else channel_username

    # Simple price extraction
    price = ""
    import re
    price_match = re.search(r'(\d[\d,\.]*)\s*(birr|etb|br|ብር)?', text, re.IGNORECASE)
    if price_match:
        price = price_match.group(0).strip()

    try:
        listing_id = db.add_listing(
            channel_username=channel_username,
            message_id=message_id,
            title=title,
            price=price,
            added_by=uid,
        )
    except Exception as e:
        if "UNIQUE" in str(e):
            await update.message.reply_text(
                f"Already added: @{channel_username}/{message_id}"
            )
        else:
            await update.message.reply_text(f"Error: {e}")
        return

    # Notify watchers
    watcher_ids = db.get_matching_watchers(title, price)
    for wid in watcher_ids:
        try:
            await context.bot.send_message(
                chat_id=wid,
                text=(
                    f"🔔 <b>New listing matches your watch!</b>\n\n"
                    f"{_listing_card(db.get_listing(listing_id))}\n"
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=_listing_keyboard(db.get_listing(listing_id)),
            )
        except Exception:
            pass

    await update.message.reply_text(
        f"✅ Added #{listing_id} from @{channel_username}/{message_id}\n"
        f"<b>{html.escape(title)}</b>"
        f"{' | ' + html.escape(price) if price else ''}\n"
        f"Notified {len(watcher_ids)} watcher(s).",
        parse_mode=ParseMode.HTML,
    )


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
            f"#{l['id']} — {html.escape(l['title'])}"
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
    """Handle @botname <query> inline searches."""
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
                    message_text=(
                        f"{card_text}\n\n"
                        f"🔗 <a href=\"{url}\">View Original Post</a>"
                    ),
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
    """Track button clicks if we ever add tracking buttons."""
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
