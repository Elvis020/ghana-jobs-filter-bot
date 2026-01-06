# GhanaJobs Bot: Telegram Job Post Filter

## Overview

A Telegram bot that monitors a group for job posting links and indicates whether the job is accessible to someone in Ghana — either worldwide remote or Ghana-based.

## Problem

Group members share job links, but most are location-restricted (US only, EU only, etc.). Members waste time clicking through only to find they're ineligible. This bot provides instant feedback on job accessibility.

## How It Works

1. Member posts a message containing a job link
2. Bot detects the link and extracts job details
3. Bot analyzes location requirements
4. Bot reacts with:
   - ✅ — Helpful (worldwide remote or Ghana-based)
   - ❌ — Not helpful (location-restricted elsewhere)
   - ❓ — Unclear (couldn't determine)

## Success Criteria

- [ ] Bot responds within 10 seconds of a job link being posted
- [ ] 90%+ accuracy on clear-cut cases (explicit "worldwide" or "US only")
- [ ] Graceful handling of sites that block scraping
- [ ] No false positives (don't mark restricted jobs as helpful)

---

## Technical Spec

### Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Bot Framework | `python-telegram-bot` v20+ |
| Scraping | `httpx` + `BeautifulSoup4`, `playwright` for JS-heavy sites |
| AI Analysis | Claude API (claude-sonnet-4-20250514) for ambiguous cases |
| Hosting | Railway / Render / VPS |
| Caching | SQLite (cache results by URL hash) |

### Project Structure

```
ghana-jobs-bot/
├── bot/
│   ├── __init__.py
│   ├── main.py              # Entry point, bot setup
│   ├── handlers.py          # Message handlers
│   ├── analyzer.py          # Job analysis logic
│   ├── scraper.py           # URL scraping
│   └── cache.py             # SQLite caching
├── config/
│   ├── __init__.py
│   └── settings.py          # Environment config
├── tests/
│   ├── test_analyzer.py
│   └── test_scraper.py
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

### Environment Variables

```bash
TELEGRAM_BOT_TOKEN=         # From @BotFather
ANTHROPIC_API_KEY=          # For Claude API (optional, for smart analysis)
LOG_LEVEL=INFO
CACHE_TTL_HOURS=24          # How long to cache job analysis results
```

---

## Core Logic

### 1. Link Detection

Detect job links from common platforms:

```python
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
]
```

### 2. Scraping Strategy

**Tier 1: Simple HTTP (fast)**
- Works for: Greenhouse, Lever, Workable, RemoteOK, WeWorkRemotely
- Use `httpx` + `BeautifulSoup`

**Tier 2: Browser automation (slower)**
- Works for: LinkedIn, Indeed, Glassdoor
- Use `playwright` with stealth

**Tier 3: Fallback**
- If scraping fails, analyze only the message text posted by user
- Or mark as ❓ (unclear)

```python
async def scrape_job(url: str) -> dict:
    """
    Returns:
        {
            "title": str,
            "company": str,
            "location": str,
            "description": str,
            "remote_policy": str,  # if found
            "raw_text": str,       # full page text for analysis
            "scrape_success": bool
        }
    """
```

### 3. Analysis Rules

**Mark as ✅ HELPFUL if any:**
- Contains: "worldwide remote", "global remote", "work from anywhere"
- Contains: "remote" AND NOT any country restriction
- Location explicitly mentions: "Ghana", "Accra", "Africa" (as eligible)
- Listed on remote-first job boards (RemoteOK, WeWorkRemotely)

**Mark as ❌ NOT HELPFUL if any:**
- Contains: "US only", "USA only", "United States only"
- Contains: "EU only", "Europe only", "UK only"
- Contains: "must be located in [specific country not Ghana]"
- Contains: "on-site only", "no remote", "in-office"
- Contains: "[Country] timezone required" (unless compatible)
- Visa sponsorship required for non-Ghana location

**Mark as ❓ UNCLEAR if:**
- Scraping failed AND no context in message
- Ambiguous language ("remote" without specifics)
- Conflicting signals

### 4. Claude API Integration (Smart Analysis)

For ambiguous cases, use Claude:

```python
ANALYSIS_PROMPT = """
Analyze this job posting for someone located in Ghana, Africa.

Determine if they can apply. Answer with ONE of:
- HELPFUL: Job is available to Ghana residents (worldwide remote, Africa included, or Ghana-based)
- NOT_HELPFUL: Job is restricted to locations that exclude Ghana
- UNCLEAR: Cannot determine from the information provided

Consider:
- "Remote" alone often means US-remote unless specified
- Timezone requirements (WAT/GMT is Ghana's timezone)
- Visa/work authorization requirements
- Company location vs job location

Job Details:
{job_content}

Answer in format:
VERDICT: [HELPFUL/NOT_HELPFUL/UNCLEAR]
REASON: [One sentence explanation]
"""
```

### 5. Caching

Cache analysis results to avoid re-scraping:

```python
# Schema
CREATE TABLE job_cache (
    url_hash TEXT PRIMARY KEY,
    url TEXT,
    verdict TEXT,  -- 'helpful', 'not_helpful', 'unclear'
    reason TEXT,
    analyzed_at TIMESTAMP,
    expires_at TIMESTAMP
);
```

---

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message with bot explanation |
| `/help` | How the bot works, what the reactions mean |
| `/check <url>` | Manually check a job URL |
| `/stats` | Show bot statistics (jobs analyzed, helpful %, etc.) |

---

## Message Flow

```
┌─────────────────────────────────────────────────────────┐
│  User posts message with job link                       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Bot detects job URL in message                         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Check cache for URL                                    │
│  ├─ HIT: Use cached verdict                             │
│  └─ MISS: Continue to scraping                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Scrape job posting                                     │
│  ├─ Success: Extract job details                        │
│  └─ Failure: Use message text only                      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Analyze with rules                                     │
│  ├─ Clear verdict: Return result                        │
│  └─ Ambiguous: Send to Claude API                       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Cache result + React to message                        │
│  ├─ ✅ Helpful                                          │
│  ├─ ❌ Not helpful                                      │
│  └─ ❓ Unclear                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Edge Cases

| Case | Handling |
|------|----------|
| Multiple links in one message | Analyze first job link only |
| Link shorteners (bit.ly, etc.) | Resolve to final URL first |
| Duplicate posts | Cache handles this |
| Bot rate limited by Telegram | Implement exponential backoff |
| Job site blocks scraping | Fall back to message text analysis |
| Job posting removed/expired | Mark as ❓, note in reply |
| Non-English job posts | Claude can handle multiple languages |

---

## Future Enhancements (Out of Scope for v1)

- [ ] Reply with brief summary (title, company, why helpful/not)
- [ ] Track which members post most helpful jobs
- [ ] Weekly digest of helpful jobs
- [ ] Support for more countries (configurable)
- [ ] Slash command to set personal location preference
- [ ] Integration with job alert channels

---

## Development Phases

### Phase 1: MVP (Start Here)
- [ ] Bot setup with BotFather
- [ ] Basic message handler detecting job links
- [ ] Rule-based analysis (no scraping, just keywords in message)
- [ ] Emoji reactions working

### Phase 2: Scraping
- [ ] Implement scrapers for top 5 job sites
- [ ] Add caching layer
- [ ] Handle failures gracefully

### Phase 3: Smart Analysis
- [ ] Integrate Claude API for ambiguous cases
- [ ] Improve accuracy based on feedback

### Phase 4: Polish
- [ ] Add commands (/help, /stats, /check)
- [ ] Logging and monitoring
- [ ] Deploy to production

---

## Getting Started

```bash
# Clone and setup
cd ghana-jobs-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your tokens

# Run
python -m bot.main
```

---

## Testing

```bash
# Run tests
pytest tests/

# Test specific URL analysis
python -m bot.analyzer "https://example.com/job/123"
```

---

**Note to Claude Code:** Start with Phase 1. Get the bot responding to messages and reacting with emojis first. Don't implement scraping until basic flow works. Use python-telegram-bot v20+ async syntax.
