"""
TeleDirectory Phase 0 — Main entry point.

Usage:
    TELEDIRECTORY_BOT_TOKEN=xxx python bot.py

Set TELEDIRECTORY_OPERATOR_IDS=123456,789012 to control who can run /add, /remove, etc.
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


def main():
    if not BOT_TOKEN:
        raise SystemExit("Set TELEDIRECTORY_BOT_TOKEN environment variable.")

    # Initialize database
    db.init_db()
    logger.info("Database initialized.")

    # Build application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ── Public commands ───────────────────────────────────
    app.add_handler(CommandHandler("start", handlers.cmd_start))
    app.add_handler(CommandHandler("help", handlers.cmd_start))
    app.add_handler(CommandHandler("search", handlers.cmd_search))
    app.add_handler(CommandHandler("watch", handlers.cmd_watch))
    app.add_handler(CommandHandler("unwatch", handlers.cmd_unwatch))
    app.add_handler(CommandHandler("mywatches", handlers.cmd_mywatches))

    # ── Operator commands ─────────────────────────────────
    app.add_handler(CommandHandler("add", handlers.cmd_add))
    app.add_handler(CommandHandler("list", handlers.cmd_list))
    app.add_handler(CommandHandler("remove", handlers.cmd_remove))
    app.add_handler(CommandHandler("sold", handlers.cmd_sold))
    app.add_handler(CommandHandler("stats", handlers.cmd_stats))
    app.add_handler(CommandHandler("forward_add", handlers.cmd_forward_add))

    # ── Inline query (@botname <query>) ───────────────────
    app.add_handler(InlineQueryHandler(handlers.inline_query))

    # ── Callback queries (button clicks) ──────────────────
    app.add_handler(CallbackQueryHandler(handlers.callback_query))

    # ── Run ───────────────────────────────────────────────
    logger.info("TeleDirectory Phase 0 bot starting…")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
