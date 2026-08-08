"""
TeleDirectory Phase 0 — Main entry point.

Bot auto-monitors Telegram channels and indexes every new post.
Buyers search in DM, find listings, click through to original posts.

Usage:
    TELEDIRECTORY_BOT_TOKEN=*** TELEDIRECTORY_OPERATOR_IDS=422511779 python bot.py
"""

import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
    CallbackQueryHandler,
    filters,
)

from config import BOT_TOKEN
import db
import handlers

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("teledirectory")

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def main():
    if not BOT_TOKEN:
        raise SystemExit("Set TELEDIRECTORY_BOT_TOKEN environment variable.")

    db.init_db()
    logger.info("Database initialized.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ── Public commands ───────────────────────────────────
    app.add_handler(CommandHandler("start", handlers.cmd_start))
    app.add_handler(CommandHandler("help", handlers.cmd_start))
    app.add_handler(CommandHandler("search", handlers.cmd_search))
    app.add_handler(CommandHandler("watch", handlers.cmd_watch))
    app.add_handler(CommandHandler("unwatch", handlers.cmd_unwatch))
    app.add_handler(CommandHandler("mywatches", handlers.cmd_mywatches))

    # ── Operator commands ─────────────────────────────────
    app.add_handler(CommandHandler("monitor", handlers.cmd_monitor))
    app.add_handler(CommandHandler("unmonitor", handlers.cmd_unmonitor))
    app.add_handler(CommandHandler("channels", handlers.cmd_channels))
    app.add_handler(CommandHandler("list", handlers.cmd_list))
    app.add_handler(CommandHandler("remove", handlers.cmd_remove))
    app.add_handler(CommandHandler("sold", handlers.cmd_sold))
    app.add_handler(CommandHandler("stats", handlers.cmd_stats))

    # ── Inline query (@botname <query>) ───────────────────
    app.add_handler(InlineQueryHandler(handlers.inline_query))

    # ── Callback queries (button clicks) ──────────────────
    app.add_handler(CallbackQueryHandler(handlers.callback_query))

    # ── Channel post handler (auto-index) ─────────────────
    # Fires when bot is admin in a channel and a new post appears
    app.add_handler(
        MessageHandler(filters.UpdateType.CHANNEL_POST, handlers.channel_post_handler),
        group=1,
    )

    # ── Plain text in DM → search ─────────────────────────
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND,
            handlers.plain_text_search,
        ),
        group=99,
    )

    logger.info("TeleDirectory Phase 0 bot starting…")
    logger.info("Auto-monitoring enabled. Use /monitor @channel to add channels.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
