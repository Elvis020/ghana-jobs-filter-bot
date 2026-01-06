"""Main entry point for Ghana Jobs Bot."""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config.settings import TELEGRAM_BOT_TOKEN, LOG_LEVEL
from bot.handlers import start_command, help_command, check_command, clearcache_command, handle_message

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL)
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    logger.info("Starting Ghana Jobs Bot...")

    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("clearcache", clearcache_command))

    # Register message handler for all text messages
    # This will detect job links automatically
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Start the bot
    logger.info("Bot is running... Press Ctrl+C to stop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
