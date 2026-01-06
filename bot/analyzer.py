"""Job posting analyzer for Ghana accessibility."""

import re
from typing import Literal, Optional
from bot.claude_analyzer import ClaudeAnalyzer

Verdict = Literal["helpful", "not_helpful", "visa_sponsorship", "unclear"]


class JobAnalyzer:
    """Analyzes job postings to determine Ghana accessibility."""

    def __init__(self, claude_api_key: Optional[str] = None):
        """
        Initialize analyzer.

        Args:
            claude_api_key: Optional Anthropic API key for smart analysis
        """
        self.claude_analyzer = ClaudeAnalyzer(claude_api_key)

    # Keywords that indicate job IS accessible to Ghana
    HELPFUL_KEYWORDS = [
        r"worldwide\s+remote",
        r"global\s+remote",
        r"work\s+from\s+anywhere",
        r"remote\s+worldwide",
        r"fully\s+remote",
        r"\bghana\b",
        r"\baccra\b",
        r"africa",
        r"any\s+location",
        r"location\s+independent",
    ]

    # Keywords that indicate visa sponsorship is offered
    VISA_SPONSORSHIP_KEYWORDS = [
        r"visa\s+sponsor(?:ship)?",
        r"sponsor(?:ing)?\s+visa",
        r"we\s+sponsor\s+visas?",
        r"willing\s+to\s+sponsor",
        r"provide\s+visa\s+sponsor(?:ship)?",
        r"offer(?:s)?\s+visa\s+sponsor(?:ship)?",
        r"relocation\s+(?:and\s+)?visa",
        r"visa\s+(?:and\s+)?relocation",
        r"h-?1b\s+sponsor(?:ship)?",
        r"work\s+authorization\s+support",
        r"immigration\s+support",
        r"assist\s+with\s+visa",
        r"help\s+with\s+visa",
        r"sponsorship\s+available",
    ]

    # Keywords that indicate job is NOT accessible to Ghana
    NOT_HELPFUL_KEYWORDS = [
        r"us\s+only",
        r"usa\s+only",
        r"united\s+states\s+only",
        r"u\.s\.\s+only",
        r"remote\s+us\b",
        r"remote\s+usa\b",
        r"eu\s+only",
        r"europe\s+only",
        r"european\s+union\s+only",
        r"remote\s+europe\b",
        r"remote\s+eu\b",
        r"europe\s+remote",
        r"uk\s+only",
        r"united\s+kingdom\s+only",
        r"remote\s+uk\b",
        r"on-?site\s+only",
        r"in-?office\s+only",
        r"no\s+remote",
        r"must\s+be\s+located\s+in",
        r"must\s+be\s+based\s+in",
        r"must\s+reside\s+in",
        r"north\s+america\s+only",
        r"canada\s+only",
        r"australia\s+only",
        r"new\s+zealand\s+only",
        r"remote\s+canada\b",
        r"remote\s+australia\b",
    ]

    # Job boards that are typically worldwide remote
    REMOTE_FIRST_DOMAINS = [
        'remoteok.com',
        'weworkremotely.com',
    ]

    async def analyze(
        self,
        text: str,
        url: str = "",
        scraped_data: Optional[dict] = None
    ) -> tuple[Verdict, str]:
        """
        Analyze job posting for Ghana accessibility.

        Args:
            text: The message text
            url: The job posting URL (optional)
            scraped_data: Scraped job data (optional)

        Returns:
            Tuple of (verdict, reason)
        """
        # Step 1: Try rule-based analysis on message text
        verdict, reason = self._rule_based_analyze(text, url)

        if verdict != "unclear":
            return verdict, reason

        # Step 2: If unclear and we have scraped data, analyze that
        if scraped_data and scraped_data.get("scrape_success"):
            scraped_text = scraped_data.get("raw_text", "")
            if scraped_text:
                verdict, reason = self._rule_based_analyze(scraped_text, url)

                if verdict != "unclear":
                    return verdict, f"{reason} (from scraped content)"

        # Step 3: If still unclear and Claude is available, use AI
        if verdict == "unclear" and self.claude_analyzer.is_available():
            # Combine message text and scraped content for Claude
            full_content = text
            if scraped_data and scraped_data.get("scrape_success"):
                full_content += "\n\n" + scraped_data.get("raw_text", "")

            verdict, reason = await self.claude_analyzer.analyze(full_content)
            return verdict, f"{reason} (AI analysis)"

        # Step 4: Return unclear if all else fails
        return verdict, reason

    def _rule_based_analyze(self, text: str, url: str = "") -> tuple[Verdict, str]:
        """
        Rule-based keyword analysis.

        Args:
            text: Text to analyze
            url: URL to check

        Returns:
            Tuple of (verdict, reason)
        """
        text_lower = text.lower()
        url_lower = url.lower()

        # Check if URL is from a remote-first job board
        if any(domain in url_lower for domain in self.REMOTE_FIRST_DOMAINS):
            return "helpful", "Posted on worldwide remote job board"

        # Check for VISA SPONSORSHIP keywords first (highest priority for relocation)
        for pattern in self.VISA_SPONSORSHIP_KEYWORDS:
            if re.search(pattern, text_lower):
                match = re.search(pattern, text_lower)
                matched_text = match.group(0) if match else pattern
                return "visa_sponsorship", f"Offers visa sponsorship: '{matched_text}'"

        # Check for NOT HELPFUL keywords (stricter check)
        for pattern in self.NOT_HELPFUL_KEYWORDS:
            if re.search(pattern, text_lower):
                match = re.search(pattern, text_lower)
                matched_text = match.group(0) if match else pattern
                return "not_helpful", f"Location restricted: '{matched_text}'"

        # Check for HELPFUL keywords
        for pattern in self.HELPFUL_KEYWORDS:
            if re.search(pattern, text_lower):
                match = re.search(pattern, text_lower)
                matched_text = match.group(0) if match else pattern
                return "helpful", f"Accessible: '{matched_text}'"

        # Check for ambiguous "remote" mention without specifics
        if re.search(r"\bremote\b", text_lower):
            # "Remote" alone is often US-remote, so mark as unclear
            return "unclear", "Mentions 'remote' but location requirements unclear"

        # If no keywords found, mark as unclear
        return "unclear", "Cannot determine location requirements from text"


# Emoji reactions for verdicts
VERDICT_EMOJIS = {
    "helpful": "✅",
    "not_helpful": "❌",
    "visa_sponsorship": "🌍",
    "unclear": "❓",
}
