# Ghana Jobs Bot

A Telegram bot that monitors group messages for job posting links and indicates whether the job is accessible to someone in Ghana (worldwide remote or Ghana-based).

## Features

- 🔍 Automatically detects job links in group messages
- ⚡ Instant analysis using rule-based keyword matching
- 🎯 Reacts with emojis:
  - ✅ Helpful (worldwide remote or Ghana-based)
  - ❌ Not helpful (location-restricted)
  - ❓ Unclear (cannot determine)
- 🌐 Supports major job platforms (LinkedIn, Indeed, Greenhouse, Lever, RemoteOK, etc.)

## Setup

### Prerequisites

- Python 3.12 (recommended for compatibility with python-telegram-bot)
- A Telegram bot token (from @BotFather)

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
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Telegram bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
   ```

### Running the Bot Locally

```bash
python -m bot.main
```

The bot will start polling for messages. Press `Ctrl+C` to stop.

**Note:** Running locally means the bot only works while your computer is on. For 24/7 availability, see the Deployment section below.

## Usage

### In Telegram

1. Add the bot to your group
2. Grant the bot permissions to read messages and react
3. Post job links in the group
4. The bot will automatically analyze and react to job postings

### Commands

- `/start` - Welcome message with bot explanation
- `/help` - Show help information
- `/check <url>` - Manually check a job URL

## How It Works

1. **Link Detection**: Bot monitors messages for URLs from known job platforms
2. **Keyword Analysis**: Analyzes message text for location indicators:
   - ✅ "worldwide remote", "global remote", "Ghana", "work from anywhere"
   - ❌ "US only", "EU only", "on-site only", "must be located in [country]"
   - ❓ Ambiguous language or insufficient information
3. **Instant Feedback**: Reacts to the message with an appropriate emoji

## Deployment (24/7 Hosting)

To keep your bot running continuously, deploy it to a hosting platform:

### Option 1: Railway (Recommended)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app) and sign up
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Add environment variable: `TELEGRAM_BOT_TOKEN=your_token_here`
   - Railway will auto-detect Python and use the `Procfile` to run the bot

3. **Done!** Your bot is now running 24/7.

**Cost:** Free tier includes 500 hours/month (~$5/month after)

### Option 2: Render

1. **Push to GitHub** (same as above)

2. **Deploy on Render:**
   - Go to [render.com](https://render.com) and sign up
   - Click "New" → "Background Worker"
   - Connect your GitHub repo
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m bot.main`
   - Add environment variable: `TELEGRAM_BOT_TOKEN`

**Cost:** Free tier available (with limitations)

### Option 3: VPS (DigitalOcean, Linode, etc.)

For more control, deploy to a VPS:

```bash
# SSH into your server
ssh user@your-server-ip

# Clone repo and setup
git clone <your-repo>
cd tbot-for-job-analysis
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file with your token
nano .env

# Run with a process manager (e.g., systemd or screen)
screen -S telegram-bot
python -m bot.main
# Press Ctrl+A, then D to detach
```

**Cost:** ~$4-5/month minimum

### Environment Variables for Deployment

Make sure to set these in your hosting platform:
- `TELEGRAM_BOT_TOKEN` (required)
- `LOG_LEVEL=INFO` (optional)
- `CACHE_TTL_HOURS=24` (optional)

## Project Structure

```
tbot-for-job-analysis/
├── bot/
│   ├── __init__.py
│   ├── main.py          # Entry point, bot setup
│   ├── handlers.py      # Message and command handlers
│   └── analyzer.py      # Job analysis logic
├── config/
│   ├── __init__.py
│   └── settings.py      # Environment configuration
├── tests/
│   └── __init__.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Development Status

✅ **Phase 1: MVP (Complete)**
- Basic message handler detecting job links
- Rule-based analysis using keywords
- Emoji reactions working

🔜 **Phase 2: Scraping (Future)**
- Web scraping for detailed job information
- Caching layer with SQLite

🔜 **Phase 3: Smart Analysis (Future)**
- Claude API integration for ambiguous cases
- Improved accuracy

## Contributing

This is a personal project, but suggestions and feedback are welcome!

## License

MIT
