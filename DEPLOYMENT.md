# Deployment Guide - Ghana Jobs Bot

## Deploying to Fly.io (FREE)

### Prerequisites
1. A Fly.io account (sign up at https://fly.io)
2. Your Telegram Bot Token (from @BotFather)
3. Your Anthropic API Key (optional, for AI analysis)

### Step 1: Install Fly CLI

**macOS:**
```bash
brew install flyctl
```

**Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows:**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

### Step 2: Authenticate with Fly.io

```bash
flyctl auth login
```

This will open your browser to complete authentication.

### Step 3: Create Your App

```bash
flyctl apps create ghana-jobs-bot
# Or use a different name if this is taken
```

### Step 4: Create a Volume for Persistent Storage

The bot uses SQLite for caching. Create a volume to persist data:

```bash
flyctl volumes create job_cache_data --region iad --size 1
```

**Note:** Choose a region close to you:
- `iad` - Washington DC (USA East)
- `lhr` - London (Europe)
- `syd` - Sydney (Australia)
- `sin` - Singapore (Asia)

### Step 5: Set Environment Variables (Secrets)

```bash
# Set your Telegram bot token
flyctl secrets set TELEGRAM_BOT_TOKEN="your_token_here"

# Set your Anthropic API key (optional but recommended)
flyctl secrets set ANTHROPIC_API_KEY="your_api_key_here"
```

### Step 6: Deploy Your Bot

```bash
flyctl deploy
```

This will:
1. Build a Docker image
2. Push it to Fly.io
3. Start your bot

### Step 7: Check Status

```bash
# Check if your app is running
flyctl status

# View logs
flyctl logs

# Open monitoring dashboard
flyctl dashboard
```

### Step 8: Monitor Your Bot

```bash
# Live tail logs
flyctl logs -a ghana-jobs-bot

# SSH into your container (for debugging)
flyctl ssh console
```

## Updating Your Bot

When you make changes to your code:

```bash
# Commit your changes
git add .
git commit -m "Updated feature X"

# Redeploy
flyctl deploy
```

## Fly.io Free Tier

- **3 shared-cpu-1x VMs** (256MB RAM each)
- **3GB persistent volume storage**
- **160GB outbound data transfer**
- **Enough for small to medium Telegram bots**

## Troubleshooting

### Bot not starting?
```bash
flyctl logs
```
Check for errors in the logs.

### Database errors?
Make sure your volume is mounted correctly:
```bash
flyctl volumes list
```

### Out of memory?
Upgrade your VM size in fly.toml:
```toml
[[vm]]
  memory_mb = 512  # Increase from 256
```
Then `flyctl deploy` again.

### Need to restart?
```bash
flyctl apps restart
```

## Scaling (if needed)

```bash
# Scale to 2 instances
flyctl scale count 2

# Scale memory
flyctl scale memory 512
```

## Cost Estimation

**Free tier includes:**
- 3 shared VMs (your bot uses 1)
- 160GB bandwidth/month

**For this bot:**
- Estimated cost: **$0/month** (within free tier)
- If you exceed free tier: ~$3-5/month

## Alternative Free Options

If Fly.io doesn't work out:

### Railway.app
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### Render.com
1. Go to https://render.com
2. Connect GitHub repo
3. Create new "Background Worker"
4. Add environment variables
5. Deploy

## Support

- Fly.io Docs: https://fly.io/docs
- Fly.io Community: https://community.fly.io
- Bot Issues: Check your logs with `flyctl logs`
