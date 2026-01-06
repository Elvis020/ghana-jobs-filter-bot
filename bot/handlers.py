"""Message handlers for the Ghana Jobs Bot."""

import logging
import re
from telegram import Update
from telegram.ext import ContextTypes

from config.settings import JOB_DOMAINS, ANTHROPIC_API_KEY, CACHE_DB_PATH, CACHE_TTL_HOURS
from bot.analyzer import JobAnalyzer, VERDICT_EMOJIS
from bot.scraper import JobScraper
from bot.cache import JobCache

logger = logging.getLogger(__name__)

# Initialize modules
analyzer = JobAnalyzer(claude_api_key=ANTHROPIC_API_KEY)
scraper = JobScraper()
cache = JobCache(db_path=CACHE_DB_PATH, ttl_hours=CACHE_TTL_HOURS)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    welcome_message = (
        "👋 Welcome to **Ghana Jobs Bot**!\n\n"
        "I help filter job postings for Ghana-based job seekers.\n\n"
        "**How it works:**\n"
        "• Post a job link in the group\n"
        "• I'll analyze if it's accessible from Ghana\n"
        "• I'll react with:\n"
        "  ✅ Helpful (worldwide remote or Ghana-based)\n"
        "  🌍 Visa sponsorship (offers relocation/visa support)\n"
        "  ❌ Not helpful (location-restricted)\n"
        "  ❓ Unclear (can't determine)\n\n"
        "Use /help for more information."
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_message = (
        "**Ghana Jobs Bot Help**\n\n"
        "**Commands:**\n"
        "• /start - Welcome message\n"
        "• /help - Show this help\n"
        "• /check <url> - Manually check a job URL\n"
        "• /clearcache - Clear cached results\n\n"
        "**Reactions:**\n"
        "• ✅ Job is accessible (worldwide remote or Ghana-based)\n"
        "• 🌍 Offers visa sponsorship (relocation/work authorization support)\n"
        "• ❌ Job is location-restricted (excludes Ghana, no sponsorship)\n"
        "• ❓ Cannot determine location requirements\n\n"
        "**Supported job sites:**\n"
        "LinkedIn, Indeed, Greenhouse, Lever, Workable, RemoteOK, "
        "WeWorkRemotely, Glassdoor, and more.\n\n"
        "Just post a job link and I'll analyze it automatically!"
    )
    await update.message.reply_text(help_message, parse_mode="Markdown")


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /check command for manual URL checking."""
    if not context.args:
        await update.message.reply_text(
            "Usage: /check <job_url>\n\nExample: /check https://jobs.example.com/position"
        )
        return

    url = context.args[0]
    message_text = " ".join(context.args)

    try:
        # 1. Check cache first
        cached = cache.get(url)
        if cached:
            logger.info(f"Using cached result for {url}")
            verdict, reason = cached.verdict, cached.reason + " (cached)"
        else:
            # 2. Try scraping
            logger.info(f"Scraping {url}...")
            scraped_data = await scraper.scrape(url)

            # 3. Analyze
            verdict, reason = await analyzer.analyze(message_text, url, scraped_data)

            # 4. Cache the result
            cache.set(url, verdict, reason, scraped_data.get("raw_text", ""))

        emoji = VERDICT_EMOJIS[verdict]
        response = f"{emoji} **{verdict.replace('_', ' ').title()}**\n\n{reason}"
        await update.message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error in check command: {e}")
        await update.message.reply_text(f"❓ Error analyzing job: {str(e)[:100]}")


async def clearcache_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /clearcache command to clear all cached results."""
    try:
        # Get stats before clearing
        stats = cache.get_stats()
        active_count = stats.get("active_entries", 0)

        # Clear all cache entries
        deleted_count = cache.clear_all()

        logger.info(f"Cache cleared by user: {deleted_count} entries removed")
        await update.message.reply_text(
            f"✅ **Cache Cleared**\n\n"
            f"Removed {deleted_count} cached results.\n"
            f"All job links will be re-analyzed fresh.",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        await update.message.reply_text(f"❌ Error clearing cache: {str(e)[:100]}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and detect job links."""
    if not update.message or not update.message.text:
        return

    message_text = update.message.text

    # Extract URLs from message
    urls = extract_urls(message_text)

    if not urls:
        return  # No URLs found, ignore message

    # Check if any URL is from a known job site
    job_urls = [url for url in urls if is_job_url(url)]

    if not job_urls:
        return  # No job URLs found

    # Analyze the first job URL
    job_url = job_urls[0]
    logger.info(f"Analyzing job URL: {job_url}")

    try:
        # 1. Check cache first
        cached = cache.get(job_url)
        if cached:
            logger.info(f"Cache HIT for {job_url}")
            verdict = cached.verdict
        else:
            logger.info(f"Cache MISS for {job_url} - scraping...")

            # 2. Try scraping
            scraped_data = await scraper.scrape(job_url)

            # 3. Analyze (rule-based + Claude if needed)
            verdict, reason = await analyzer.analyze(message_text, job_url, scraped_data)

            logger.info(f"Verdict: {verdict} - {reason}")

            # 4. Cache the result
            cache.set(job_url, verdict, reason, scraped_data.get("raw_text", ""))

        # 5. React to the message with emoji
        emoji = VERDICT_EMOJIS[verdict]
        await update.message.set_reaction(emoji)

    except Exception as e:
        logger.error(f"Error analyzing job: {e}", exc_info=True)
        # React with unclear emoji if analysis fails
        await update.message.set_reaction("❓")


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text."""
    # Regex pattern to match URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return urls


def is_job_url(url: str) -> bool:
    """Check if URL is from a known job site."""
    url_lower = url.lower()
    return any(domain in url_lower for domain in JOB_DOMAINS)
