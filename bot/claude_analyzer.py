"""Claude API integration for smart job analysis."""

import logging
from typing import Optional, Tuple
from anthropic import Anthropic, AnthropicError

logger = logging.getLogger(__name__)


class ClaudeAnalyzer:
    """Uses Claude API for intelligent job analysis."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude analyzer.

        Args:
            api_key: Anthropic API key (optional)
        """
        self.api_key = api_key
        self.client = Anthropic(api_key=api_key) if api_key else None

    def is_available(self) -> bool:
        """Check if Claude API is available."""
        return self.client is not None and self.api_key is not None

    async def analyze(self, job_content: str) -> Tuple[str, str]:
        """
        Analyze job content using Claude API.

        Args:
            job_content: The job posting content (scraped or message text)

        Returns:
            Tuple of (verdict, reason)
            verdict: "helpful" | "not_helpful" | "visa_sponsorship" | "unclear"
            reason: Explanation for the verdict
        """
        if not self.is_available():
            logger.warning("Claude API not available - no API key configured")
            return "unclear", "AI analysis unavailable (no API key)"

        try:
            prompt = self._build_prompt(job_content)

            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            response_text = message.content[0].text
            verdict, reason = self._parse_response(response_text)

            logger.info(f"Claude analysis: {verdict} - {reason[:50]}...")
            return verdict, reason

        except AnthropicError as e:
            logger.error(f"Claude API error: {e}")
            return "unclear", f"AI analysis failed: {str(e)[:50]}"

        except Exception as e:
            logger.error(f"Unexpected error in Claude analysis: {e}")
            return "unclear", "AI analysis encountered an error"

    def _build_prompt(self, job_content: str) -> str:
        """Build the analysis prompt for Claude."""
        # Truncate content if too long (to avoid token limits)
        max_chars = 8000
        if len(job_content) > max_chars:
            job_content = job_content[:max_chars] + "...[truncated]"

        return f"""Analyze this job posting for someone located in Ghana, Africa.

Determine if they can apply. Answer with ONE of:
- HELPFUL: Job is available to Ghana residents (worldwide remote, Africa included, or Ghana-based)
- VISA_SPONSORSHIP: Job offers visa sponsorship/relocation assistance (even if initially location-restricted)
- NOT_HELPFUL: Job is restricted to locations that exclude Ghana AND no visa sponsorship offered
- UNCLEAR: Cannot determine from the information provided

Consider:
- "Remote" alone often means US-remote unless specified
- Timezone requirements (WAT/GMT is Ghana's timezone, GMT+0)
- Visa/work authorization/sponsorship (H-1B, work permits, immigration support, relocation packages)
- Company location vs job location
- Explicit location restrictions
- Even if job requires specific location initially, visa sponsorship makes it accessible

IMPORTANT: If visa sponsorship or relocation assistance is mentioned, choose VISA_SPONSORSHIP even if there are location restrictions.

Job Details:
{job_content}

Answer in format:
VERDICT: [HELPFUL/VISA_SPONSORSHIP/NOT_HELPFUL/UNCLEAR]
REASON: [One sentence explanation]"""

    def _parse_response(self, response: str) -> Tuple[str, str]:
        """
        Parse Claude's response into verdict and reason.

        Args:
            response: Raw response from Claude

        Returns:
            Tuple of (verdict, reason)
        """
        try:
            lines = response.strip().split("\n")

            verdict_line = ""
            reason_line = ""

            for line in lines:
                if line.startswith("VERDICT:"):
                    verdict_line = line.replace("VERDICT:", "").strip().upper()
                elif line.startswith("REASON:"):
                    reason_line = line.replace("REASON:", "").strip()

            # Map verdict to our format
            if "VISA_SPONSORSHIP" in verdict_line or "VISA SPONSORSHIP" in verdict_line:
                verdict = "visa_sponsorship"
            elif "HELPFUL" in verdict_line and "NOT" not in verdict_line:
                verdict = "helpful"
            elif "NOT_HELPFUL" in verdict_line or "NOT HELPFUL" in verdict_line:
                verdict = "not_helpful"
            else:
                verdict = "unclear"

            reason = reason_line if reason_line else "Analysis completed"

            return verdict, reason

        except Exception as e:
            logger.error(f"Error parsing Claude response: {e}")
            return "unclear", "Could not parse AI analysis"
