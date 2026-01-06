# Ghana Jobs Bot - Usage Guide

## 🚀 Quick Start

The bot now uses **manual commands only** - no automatic detection.

### Basic Usage

When you see a job posting in your group:

```
/check https://careers.company.com/job/12345
```

That's it! The bot will:
1. ✅ Scrape the job posting
2. 🤖 Analyze if it's accessible from Ghana
3. 💬 Reply with a verdict and reason

---

## 📋 Commands

### `/start`
Shows welcome message with usage instructions.

**Example:**
```
/start
```

### `/check <url>`
Analyze any job posting URL.

**Examples:**
```
/check https://careers.google.com/jobs/results/123
/check https://linkedin.com/jobs/view/456
/check https://jobs.company.com/positions/789
```

**Response:**
The bot will reply with:
- ✅ **Helpful** - Job is accessible (worldwide remote/Ghana-based)
- 🌍 **Visa Sponsorship** - Job offers relocation/visa support
- ❌ **Not Helpful** - Location-restricted, excludes Ghana
- ❓ **Unclear** - Cannot determine requirements

### `/help`
Show detailed help with examples.

**Example:**
```
/help
```

### `/clearcache`
Clear all cached job analyses (admin/debugging).

**Example:**
```
/clearcache
```

---

## 💡 Usage in Groups

### Scenario 1: Someone shares a job
```
User: "Check this out!"
User: https://careers.stripe.com/jobs/123

You: /check https://careers.stripe.com/jobs/123
Bot: ✅ Helpful
     Job is accessible: 'remote worldwide'
```

### Scenario 2: Reply to a message
```
User: "Anyone interested?"
      https://jobs.company.com/position

You: /check https://jobs.company.com/position
     (Reply to their message)
Bot: ❌ Not helpful
     Location restricted: 'us only'
```

### Scenario 3: Multiple jobs
```
You: /check https://job1.com
Bot: ✅ Helpful

You: /check https://job2.com
Bot: ❌ Not helpful

You: /check https://job3.com
Bot: 🌍 Visa sponsorship
```

---

## 🎯 Pro Tips

1. **Cache System**: Results are cached for 24 hours. Same URL = instant response.

2. **Works with most job sites**:
   - LinkedIn, Indeed, Greenhouse
   - Lever, Workable, RemoteOK
   - Company career pages (careers.*, jobs.*)

3. **AI-Powered**: Uses Claude AI for intelligent analysis when simple rules aren't enough.

4. **Copy-Paste Friendly**: Just copy the URL and type `/check` before it.

5. **Group-Friendly**: Works in both private chats and groups.

---

## 🔧 Troubleshooting

### Bot not responding?
1. Make sure you're using `/check` command (not just posting the URL)
2. Check the URL is complete (starts with `https://`)
3. Try `/start` to verify bot is online

### Getting "unclear" results?
- Job posting might not clearly state location requirements
- Try checking the actual job page manually
- Some sites have anti-scraping protection

### Cache issues?
Use `/clearcache` to force re-analysis of all jobs.

---

## 📊 How It Works

1. **Detection**: You use `/check <url>` command
2. **Scraping**: Bot fetches and extracts job details
3. **Rule-Based Check**: Looks for keywords like "remote worldwide", "visa sponsorship", "US only"
4. **AI Analysis**: If unclear, Claude AI reads the full posting
5. **Response**: Bot replies with verdict and explanation

---

## 🆘 Need Help?

- Type `/help` for in-bot help
- Check if bot is running: `/start`
- Ask in your group for assistance

---

## 🚀 Running the Bot

### Local Testing
```bash
./venv/bin/python -m bot.main
```

### Deployed (Fly.io)
```bash
flyctl deploy
flyctl logs
```

See `DEPLOYMENT.md` for full deployment guide.
