# Ghana Jobs Bot

A Telegram bot that analyzes job postings to determine if they're accessible to Ghana-based job seekers. Use `/check <url>` to instantly analyze any job posting for location requirements and visa sponsorship.

## Features

- 🎯 **Manual command-based analysis** - Explicit control with `/check <url>`
- ⚡ **Instant analysis** - Rule-based keyword matching + AI-powered analysis
- 🌍 **Visa sponsorship detection** - Identifies jobs offering relocation support
- 💾 **Smart caching** - 24-hour cache for faster repeat lookups
- 🤖 **AI-powered** - Claude AI integration for intelligent analysis
- 📊 **Clear verdicts:**
  - ✅ Helpful (worldwide remote or Ghana-based)
  - 🌍 Visa sponsorship (offers relocation/visa support)
  - ❌ Not helpful (location-restricted)
  - ❓ Unclear (cannot determine)
- 🌐 **Supports major job platforms** (LinkedIn, Indeed, Greenhouse, Lever, RemoteOK, etc.)

## Setup

### Prerequisites

- Python 3.12 (required for compatibility with python-telegram-bot)
- A Telegram bot token (from @BotFather)
- Anthropic API key (optional, for AI analysis)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd tbot-for-job-analysis
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file with:
   ```bash
   TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
   ANTHROPIC_API_KEY=your_claude_api_key  # Optional but recommended
   LOG_LEVEL=INFO
   CACHE_TTL_HOURS=24
   CACHE_DB_PATH=job_cache.db
   ```

### Running the Bot Locally

```bash
./venv/bin/python -m bot.main
```

The bot will start polling for messages. Press `Ctrl+C` to stop.

**Note:** Running locally means the bot only works while your computer is on. For 24/7 availability, deploy to Fly.io (see below).

## Usage

### Commands

The bot uses **manual commands only** - no automatic detection.

**Main command:**
```
/check <job_url>
```

**Example:**
```
/check https://careers.company.com/job/12345
```

**Other commands:**
- `/start` - Show welcome message and usage guide
- `/help` - Show detailed help with examples
- `/clearcache` - Clear all cached results

### In Telegram Groups

When someone shares a job posting:
```
User: "Check this out!"
      https://careers.stripe.com/jobs/123

You:  /check https://careers.stripe.com/jobs/123

Bot:  ✅ Helpful
      Job is accessible: 'remote worldwide'
```

## How It Works

1. **Command Invocation**: User runs `/check <url>`
2. **Web Scraping**: Bot fetches and extracts job posting content
3. **Rule-Based Analysis**: Checks for keywords:
   - 🌍 "visa sponsorship", "H-1B", "relocation support"
   - ✅ "worldwide remote", "global remote", "Ghana", "work from anywhere"
   - ❌ "US only", "EU only", "on-site only", "must be located in [country]"
4. **AI Analysis**: If unclear, Claude AI reads the full posting for smart analysis
5. **Cached Results**: Stores results for 24 hours for instant repeat lookups
6. **Response**: Bot replies with verdict and detailed explanation

## Deployment (24/7 on Fly.io)

Deploy your bot to Fly.io for free 24/7 hosting.

### Quick Start

1. **Install Fly CLI:**
   ```bash
   # macOS
   brew install flyctl

   # Linux
   curl -L https://fly.io/install.sh | sh

   # Windows
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Login and create app:**
   ```bash
   flyctl auth login
   flyctl apps create ghana-jobs-bot  # Or choose your own name
   ```

3. **Create persistent volume:**
   ```bash
   flyctl volumes create job_cache_data --region iad --size 1
   ```

   **Regions:** `iad` (USA East), `lhr` (London), `sin` (Singapore), `syd` (Sydney)

4. **Set secrets:**
   ```bash
   flyctl secrets set TELEGRAM_BOT_TOKEN="your_bot_token"
   flyctl secrets set ANTHROPIC_API_KEY="your_claude_key"  # Optional
   ```

5. **Deploy:**
   ```bash
   flyctl deploy
   ```

6. **Monitor:**
   ```bash
   flyctl status      # Check app status
   flyctl logs        # View live logs
   flyctl dashboard   # Open web dashboard
   ```

### Updating Your Bot

When you make changes:
```bash
git add .
git commit -m "Your changes"
flyctl deploy
```

### Cost

**Free tier includes:**
- 3 shared-cpu VMs (256MB RAM each)
- 3GB persistent storage
- 160GB bandwidth/month

**Your bot:** $0/month (within free tier)

### Troubleshooting

**Bot not starting?**
```bash
flyctl logs  # Check for errors
```

**Need to restart?**
```bash
flyctl apps restart
```

**Database issues?**
```bash
flyctl volumes list  # Verify volume is mounted
```

See `DEPLOYMENT.md` for the complete deployment guide with detailed troubleshooting.

## Project Structure

```
tbot-for-job-analysis/
├── bot/
│   ├── __init__.py
│   ├── main.py            # Entry point, bot setup
│   ├── handlers.py        # Command handlers (/start, /check, etc.)
│   ├── analyzer.py        # Job analysis logic (rule-based)
│   ├── claude_analyzer.py # AI-powered analysis
│   ├── scraper.py         # Web scraping for job postings
│   └── cache.py           # SQLite caching layer
├── config/
│   ├── __init__.py
│   └── settings.py        # Environment configuration
├── tests/
│   └── __init__.py
├── requirements.txt       # Python dependencies
├── runtime.txt           # Python version for deployment
├── Dockerfile            # Docker configuration for Fly.io
├── fly.toml              # Fly.io deployment config
├── .gitignore
├── DEPLOYMENT.md         # Detailed deployment guide
├── USAGE_GUIDE.md        # Complete usage documentation
└── README.md             # This file
```

## Development Status

✅ **Core Features (Complete)**
- Manual command-based operation (`/check <url>`)
- Rule-based keyword analysis
- Web scraping for job content extraction
- SQLite caching layer (24-hour TTL)
- Claude AI integration for intelligent analysis
- Visa sponsorship detection
- Fly.io deployment ready

📋 **Current Version:** 1.0.0
- Manual operation only (no automatic detection)
- Smart caching for performance
- AI-powered analysis for ambiguous cases

## Contributing

This is a personal project, but suggestions and feedback are welcome!

## License

MIT
