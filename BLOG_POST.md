# Building a Smart Job Filter Bot for Remote Work Seekers

## How It Started: A Simple Frustration

I'm part of a Telegram group where a friend regularly posts job opportunities in a sub-channel called "Jobs." Every day, new links. New possibilities. New hope.

But here's what kept happening:

1. Click link
2. Read through the entire job description
3. Get excited about the role
4. Scroll down to location requirements
5. See "US-based only" or "Remote (EU timezone required)"
6. Close tab. Feel frustrated.

This wasn't a one-time thing. It was happening **multiple times a day**. Each click represented wasted time - time I could've spent actually applying to jobs I *could* get, or learning a new skill, or literally anything else.

The worst part? The word "remote" in the job title. It sounds so promising! Until you realize "remote" often means "remote within our specific country/timezone/continent."

One evening, after clicking through yet another "remote" job that turned out to be California-only, I thought: **"There has to be a better way."**

That's when I decided to build **Ghana Jobs Bot** - a Telegram bot that checks if a job is actually accessible from Ghana *before* I waste my time reading it.

## Why This Matters

This problem isn't unique to Ghana. If you're looking for remote work from:
- Africa
- South America
- Asia (outside specific hubs)
- Eastern Europe
- Anywhere that's not US/EU/UK

...you know this pain. Job boards are filled with "remote" positions that quietly exclude you. The frustration of repeatedly clicking, reading, hoping, only to be disappointed by hidden location requirements is universal.

My friend sharing jobs in our Telegram group was trying to help. But without a way to pre-filter, they were unknowingly sharing opportunities most of us couldn't access. **Ghana Jobs Bot** was my solution to this shared problem.

## What It Does

The bot uses a simple command:
```
/check https://careers.company.com/job/12345
```

And replies with one of four verdicts:
- ✅ **Helpful** - Worldwide remote or Ghana-based
- 🌍 **Visa Sponsorship** - Offers relocation support
- ❌ **Not Helpful** - Location-restricted, excludes Ghana
- ❓ **Unclear** - Cannot determine requirements

## The Technical Journey

### Stack & Architecture

**Core Technologies:**
- Python 3.12 + python-telegram-bot
- Claude AI (Anthropic) for intelligent analysis
- SQLite for caching results
- Fly.io for 24/7 hosting

**Why These Choices?**

I chose **polling mode** over webhooks because:
1. Simpler setup (no domain/SSL required)
2. Perfect for low-to-medium traffic
3. Works great with Fly.io's persistent containers
4. Easier to debug during development

For the AI component, I went with **Claude** because it excels at nuanced text analysis - exactly what's needed for parsing job requirements where "remote" could mean anything from "worldwide" to "remote-ish in our San Francisco office."

### Architecture Overview

```
User sends /check command
    ↓
Bot scrapes job posting
    ↓
Rule-based keyword check
    ↓
Still unclear? → Claude AI analysis
    ↓
Cache result (24 hours)
    ↓
Reply to user
```

### Challenge #1: URL Detection That Actually Works

**Initial Approach:**
```python
JOB_DOMAINS = [
    'linkedin.com/jobs',
    'indeed.com',
    '/jobs/',  # Generic pattern
]
```

**The Problem:**
This missed tons of real job sites! `careers.jackhenry.com/job/...` wouldn't match because I only checked for `/jobs/` (plural), not `/job/` (singular).

**The Solution:**
Add comprehensive patterns:
```python
JOB_DOMAINS = [
    '/jobs/',      # Plural
    '/job/',       # Singular
    '/careers/',   # Path-based
    'careers.',    # Subdomain
    'jobs.',       # jobs.company.com
    'apply.',      # Application portals
]
```

This catches 95% of job sites while keeping false positives low.

### Challenge #2: Automatic vs. Manual Operation

**What I Learned the Hard Way:**

I initially built the bot to automatically detect job links in group messages. Seemed smart, right? Wrong.

**Problems:**
1. **Privacy Mode** - Telegram bots can't see regular messages by default
2. **Noise** - Bot reacting to every link cluttered the chat
3. **Unclear intent** - Users didn't know when the bot would activate
4. **False positives** - Reacting to non-job URLs was annoying

**The Pivot:**
Switched to **manual commands only**:
```python
# Before (automatic)
application.add_handler(
    MessageHandler(filters.TEXT, handle_message)
)

# After (manual)
application.add_handler(
    CommandHandler("check", check_command)
)
```

This made the bot:
- More reliable (no privacy mode issues)
- Less noisy (users control when it activates)
- Clearer to use (explicit `/check` command)
- Better UX overall

### Challenge #3: Visa Sponsorship Detection

**The Insight:**

A job that says "US only" but offers visa sponsorship is actually *more valuable* than one with vague requirements. I needed to detect and prioritize these.

**Implementation:**
```python
VISA_SPONSORSHIP_KEYWORDS = [
    r"visa\s+sponsor(?:ship)?",
    r"h-?1b\s+sponsor(?:ship)?",
    r"relocation\s+(?:and\s+)?visa",
    r"immigration\s+support",
    r"willing\s+to\s+sponsor",
]
```

**Detection Priority:**
1. Check for visa sponsorship **first**
2. Then check location restrictions
3. Then check for worldwide remote
4. Finally, use AI if still unclear

This ensures jobs like "US-based with H-1B sponsorship" get flagged as opportunities, not rejections.

### Challenge #4: Claude AI Integration

**The Smart Fallback:**

When keyword matching fails, Claude AI reads the full job posting:

```python
prompt = f"""Analyze this job posting for someone in Ghana, Africa.

Determine if they can apply. Answer with ONE of:
- HELPFUL: Available to Ghana residents
- VISA_SPONSORSHIP: Offers visa/relocation support
- NOT_HELPFUL: Restricted, excludes Ghana
- UNCLEAR: Cannot determine

Consider:
- "Remote" alone often means US-remote
- Timezone requirements (Ghana = GMT+0)
- Visa/work authorization mentions

Job Details:
{job_content}

Answer in format:
VERDICT: [HELPFUL/VISA_SPONSORSHIP/NOT_HELPFUL/UNCLEAR]
REASON: [One sentence explanation]
"""
```

This hybrid approach (rules + AI) gives:
- ⚡ Fast responses (cached keyword matches)
- 🎯 High accuracy (AI handles edge cases)
- 💰 Cost-effective (AI only when needed)

### Challenge #5: Deployment & Configuration

**The Region Mismatch:**

Deploying to Fly.io, I hit this error:
```
Error: Process group needs volumes in region 'lhr'
but volume exists in region 'iad'
```

**What Happened:**
- My app had machines in London (`lhr`)
- I created a volume in Washington DC (`iad`)
- Fly.io volumes must be in the same region as machines!

**The Fix:**
```bash
# Delete iad volume
flyctl volumes destroy vol_xxx

# Create volume in lhr (where machines are)
flyctl volumes create job_cache_data --region lhr --size 1

# Update fly.toml
primary_region = "lhr"

# Deploy
flyctl deploy
```

**Lesson:** Always check where your machines are before creating volumes!

## Key Features

### 1. Smart Caching
```python
class JobCache:
    def get(self, url: str) -> Optional[CachedResult]:
        """Check cache for 24-hour results"""

    def set(self, url: str, verdict: str, reason: str):
        """Store analysis for reuse"""
```

Results cached for 24 hours = instant responses for repeat URLs.

### 2. Command Menu
```python
async def post_init(application: Application):
    """Set bot commands on startup"""
    commands = [
        BotCommand("start", "Show welcome and usage"),
        BotCommand("help", "Detailed help with examples"),
        BotCommand("check", "Analyze a job URL"),
        BotCommand("clearcache", "Clear cached results"),
    ]
    await application.bot.set_my_commands(commands)
```

Users see available commands when they type `/` in Telegram!

### 3. Comprehensive Error Handling
```python
try:
    scraped_data = await scraper.scrape(url)
    verdict, reason = await analyzer.analyze(url, scraped_data)
    cache.set(url, verdict, reason)
except Exception as e:
    logger.error(f"Analysis failed: {e}")
    return "unclear", "Analysis encountered an error"
```

Graceful degradation keeps the bot running even when scraping fails.

## Deployment on Fly.io

**Why Fly.io?**
- Free tier includes 3 VMs (I use 1)
- Persistent volumes for SQLite
- Always-on (perfect for polling bots)
- Simple CLI deployment

**Setup:**
```bash
# Install CLI
brew install flyctl

# Login & create app
flyctl auth login
flyctl apps create ghana-jobs-filter-bot

# Create persistent volume
flyctl volumes create job_cache_data --region lhr --size 1

# Set secrets
flyctl secrets set \
  TELEGRAM_BOT_TOKEN="your_token" \
  ANTHROPIC_API_KEY="your_key"

# Deploy
flyctl deploy
```

**Cost:** $0/month (within free tier)

## Lessons Learned

### 1. Start Simple, Iterate
Don't over-engineer. I started with basic keyword matching, added caching when needed, then AI for edge cases. Each feature was added to solve a real problem.

### 2. Manual > Automatic (Sometimes)
Automatic features seem cool but manual commands often provide better UX. Users want control, not magic that sometimes works.

### 3. Prioritize Detection Order Matters
Checking for visa sponsorship *before* location restrictions made a huge difference. The order of your conditional logic shapes the user experience.

### 4. Cache Aggressively
Job postings don't change hourly. 24-hour caching reduced API calls by 80% while maintaining accuracy.

### 5. Graceful Degradation
When scraping fails, fall back to message text analysis. When AI fails, return "unclear" not an error. Always have a fallback.

## The Results

**What Works Well:**
- ✅ Instant responses for cached URLs
- ✅ High accuracy (keyword + AI combo)
- ✅ Visa sponsorship detection is a game-changer
- ✅ Runs 24/7 for free on Fly.io
- ✅ Clear, actionable verdicts

**What Could Be Better:**
- Some job sites have anti-scraping protection
- Generic "remote" mentions still sometimes unclear
- Could add support for more languages (currently English-focused)

## Real-World Impact

Since deploying the bot to our Telegram group:

**Time Saved:** Instead of 5-10 minutes per job post (reading, getting excited, discovering restrictions), it now takes **10 seconds** to check. That's 30-50x faster.

**Focus Shift:** Group members now spend time on jobs they can *actually* apply to, rather than getting demoralized by constant rejections.

**Better Conversations:** My friend who shares jobs can now use the bot first, filtering before posting. The "Jobs" channel now has higher-quality, accessible opportunities.

**Unexpected Benefit:** The 🌍 visa sponsorship detection opened eyes to opportunities we were dismissing. "US-based with H-1B sponsorship" isn't an automatic no - it's a different type of yes.

The bot didn't just save time. It changed how we approach job hunting.

## Code Highlights

**The Analysis Pipeline:**
```python
async def analyze(self, text: str, url: str, scraped_data: Optional[dict]):
    # 1. Try rule-based on message text
    verdict, reason = self._rule_based_analyze(text, url)
    if verdict != "unclear":
        return verdict, reason

    # 2. Try scraped content
    if scraped_data and scraped_data.get("scrape_success"):
        verdict, reason = self._rule_based_analyze(
            scraped_data["raw_text"], url
        )
        if verdict != "unclear":
            return verdict, f"{reason} (from scraped content)"

    # 3. Fall back to Claude AI
    if self.claude_analyzer.is_available():
        verdict, reason = await self.claude_analyzer.analyze(full_content)
        return verdict, f"{reason} (AI analysis)"

    return "unclear", "Cannot determine requirements"
```

**Clean separation of concerns:**
- `analyzer.py` - Rule-based logic
- `claude_analyzer.py` - AI integration
- `scraper.py` - Web scraping
- `cache.py` - SQLite caching
- `handlers.py` - Telegram commands

## Try It Yourself

The bot is live! Add it to your Telegram:
**@ghanajobs_filter_bot**

## Future Improvements

**Potential Features:**
1. **Job Board Integrations** - Direct API access to LinkedIn, Indeed
2. **User Preferences** - Configure your location/requirements
3. **Saved Searches** - Get notified of new matching jobs
4. **Analytics Dashboard** - See trends in remote job availability
5. **Multi-language Support** - Analyze jobs in different languages

## Conclusion

What started as personal frustration - wasting time clicking job links that weren't accessible - turned into a tool that helps my entire Telegram group.

Building this bot taught me that **the best solutions come from solving your own problems**. I wasn't building for some hypothetical user with hypothetical needs. I was building for *me*, frustrated after clicking yet another "remote" job that turned out to be California-only.

The key insights:
- **Solve your own problem first** - If it frustrates you, it frustrates others
- **Manual control > automatic "magic"** - Users want reliability, not cleverness
- **Hybrid AI + rules > pure AI or pure rules** - Combine strengths of both
- **Good caching > fast APIs** - Speed matters, but smart caching beats optimization
- **Iterate based on reality** - Real usage teaches more than planning

If you're building a similar bot, start with your actual pain point. Don't build what you think people need - build what you know you need, because you've felt that pain multiple times a day.

That Telegram "Jobs" channel that used to frustrate me? Now it's actually useful. And that's worth every line of code.

---

**Tech Stack Summary:**
- Python 3.12
- python-telegram-bot (polling mode)
- Claude AI (Anthropic)
- SQLite (caching)
- Fly.io (hosting)

**Links:**
- [Source Code](#)
- [Deployment Guide](DEPLOYMENT.md)
- [Usage Guide](USAGE_GUIDE.md)

**Questions?** Feel free to reach out or open an issue!

---

*Built with curiosity, debugged with patience, deployed with joy.* 🚀
