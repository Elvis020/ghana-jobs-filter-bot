"""Main entry point for Ghana Jobs Bot."""

import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config.settings import TELEGRAM_BOT_TOKEN, LOG_LEVEL
from bot.handlers import start_command, help_command, check_command, clearcache_command

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL)
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Set bot commands after initialization."""
    commands = [
        BotCommand("start", "Show welcome message and usage guide"),
        BotCommand("help", "Show detailed help and examples"),
        BotCommand("check", "Analyze a job URL: /check <url>"),
        BotCommand("clearcache", "Clear all cached results"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands set successfully")


def main() -> None:
    """Start the bot."""
    logger.info("Starting Ghana Jobs Bot...")

    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("clearcache", clearcache_command))

    # Note: Automatic job link detection is disabled
    # Users must use /check <url> command to analyze jobs

    # Start the bot
    logger.info("Bot is running... Press Ctrl+C to stop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
