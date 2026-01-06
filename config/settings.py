"""Configuration settings for Ghana Jobs Bot."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

# Optional: Anthropic API (for Phase 2+)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Bot Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "24"))
CACHE_DB_PATH = os.getenv("CACHE_DB_PATH", "job_cache.db")
SCRAPE_TIMEOUT = int(os.getenv("SCRAPE_TIMEOUT", "10"))

# Job site domains to detect
JOB_DOMAINS = [
    'linkedin.com/jobs',
    'indeed.com',
    'greenhouse.io',
    'lever.co',
    'jobs.lever.co',
    'workable.com',
    'angel.co/jobs',
    'wellfound.com',
    'remoteok.com',
    'weworkremotely.com',
    'glassdoor.com/job',
    'ziprecruiter.com',
    'careers.google.com',
    'jobs.apple.com',
    'amazon.jobs',
    'apply.workable.com',
    'job-boards.greenhouse.io',
    'boards.greenhouse.io',
    '/jobs/',  # Generic pattern for careers.*.com/jobs/ URLs
    '/careers/',  # Generic pattern for *.com/careers/ URLs
]
