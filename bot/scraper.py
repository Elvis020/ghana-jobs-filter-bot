"""Web scraper for job postings."""

import logging
import httpx
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class JobScraper:
    """Scrapes job postings from various job sites."""

    def __init__(self, timeout: int = 10):
        """
        Initialize the scraper.

        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

    async def scrape(self, url: str) -> dict:
        """
        Scrape a job posting URL.

        Args:
            url: The job posting URL

        Returns:
            Dictionary with job data:
            {
                "title": str,
                "company": str,
                "location": str,
                "description": str,
                "raw_text": str,
                "scrape_success": bool
            }
        """
        try:
            domain = urlparse(url).netloc.lower()

            # Route to appropriate scraper based on domain
            if "greenhouse.io" in domain:
                return await self._scrape_greenhouse(url)
            elif "lever.co" in domain:
                return await self._scrape_lever(url)
            elif "workable.com" in domain:
                return await self._scrape_workable(url)
            elif "remoteok" in domain:
                return await self._scrape_remoteok(url)
            elif "weworkremotely.com" in domain:
                return await self._scrape_weworkremotely(url)
            else:
                # Generic scraper for unknown sites
                return await self._scrape_generic(url)

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return self._empty_result()

    async def _scrape_greenhouse(self, url: str) -> dict:
        """Scrape Greenhouse job postings."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers, follow_redirects=True)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title_elem = soup.find("h1", class_="app-title")
            title = title_elem.get_text(strip=True) if title_elem else ""

            # Extract company
            company_elem = soup.find("span", class_="company-name")
            company = company_elem.get_text(strip=True) if company_elem else ""

            # Extract location
            location_elem = soup.find("div", class_="location")
            location = location_elem.get_text(strip=True) if location_elem else ""

            # Extract description
            content_elem = soup.find("div", id="content")
            description = content_elem.get_text(separator=" ", strip=True) if content_elem else ""

            # Get all text for analysis
            raw_text = soup.get_text(separator=" ", strip=True)

            logger.info(f"Successfully scraped Greenhouse job: {title}")

            return {
                "title": title,
                "company": company,
                "location": location,
                "description": description,
                "raw_text": raw_text,
                "scrape_success": True
            }

        except Exception as e:
            logger.warning(f"Failed to scrape Greenhouse URL {url}: {e}")
            return self._empty_result()

    async def _scrape_lever(self, url: str) -> dict:
        """Scrape Lever job postings."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers, follow_redirects=True)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title_elem = soup.find("h2", class_="posting-headline")
            title = title_elem.get_text(strip=True) if title_elem else ""

            # Extract company (from meta tag or header)
            company_elem = soup.find("meta", property="og:site_name")
            company = company_elem.get("content", "") if company_elem else ""

            # Extract location
            location_elem = soup.find("div", class_="posting-categories")
            location = location_elem.get_text(strip=True) if location_elem else ""

            # Extract description
            content_elem = soup.find("div", class_="posting-description")
            description = content_elem.get_text(separator=" ", strip=True) if content_elem else ""

            # Get all text
            raw_text = soup.get_text(separator=" ", strip=True)

            logger.info(f"Successfully scraped Lever job: {title}")

            return {
                "title": title,
                "company": company,
                "location": location,
                "description": description,
                "raw_text": raw_text,
                "scrape_success": True
            }

        except Exception as e:
            logger.warning(f"Failed to scrape Lever URL {url}: {e}")
            return self._empty_result()

    async def _scrape_workable(self, url: str) -> dict:
        """Scrape Workable job postings."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers, follow_redirects=True)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title_elem = soup.find("h1")
            title = title_elem.get_text(strip=True) if title_elem else ""

            # Extract company
            company_elem = soup.find("span", {"data-ui": "company-name"})
            company = company_elem.get_text(strip=True) if company_elem else ""

            # Extract location
            location_elem = soup.find("span", {"data-ui": "job-location"})
            location = location_elem.get_text(strip=True) if location_elem else ""

            # Extract description
            description_elem = soup.find("div", {"data-ui": "job-description"})
            description = description_elem.get_text(separator=" ", strip=True) if description_elem else ""

            # Get all text
            raw_text = soup.get_text(separator=" ", strip=True)

            logger.info(f"Successfully scraped Workable job: {title}")

            return {
                "title": title,
                "company": company,
                "location": location,
                "description": description,
                "raw_text": raw_text,
                "scrape_success": True
            }

        except Exception as e:
            logger.warning(f"Failed to scrape Workable URL {url}: {e}")
            return self._empty_result()

    async def _scrape_remoteok(self, url: str) -> dict:
        """Scrape RemoteOK job postings."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers, follow_redirects=True)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title_elem = soup.find("h2", itemprop="title")
            title = title_elem.get_text(strip=True) if title_elem else ""

            # Extract company
            company_elem = soup.find("h3", itemprop="name")
            company = company_elem.get_text(strip=True) if company_elem else ""

            # Extract location
            location_elem = soup.find("div", class_="location")
            location = location_elem.get_text(strip=True) if location_elem else "Worldwide Remote"

            # Get all text
            raw_text = soup.get_text(separator=" ", strip=True)

            logger.info(f"Successfully scraped RemoteOK job: {title}")

            return {
                "title": title,
                "company": company,
                "location": location,
                "description": raw_text,
                "raw_text": raw_text,
                "scrape_success": True
            }

        except Exception as e:
            logger.warning(f"Failed to scrape RemoteOK URL {url}: {e}")
            return self._empty_result()

    async def _scrape_weworkremotely(self, url: str) -> dict:
        """Scrape WeWorkRemotely job postings."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers, follow_redirects=True)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title_elem = soup.find("h1", class_="listing-headline")
            title = title_elem.get_text(strip=True) if title_elem else ""

            # Extract company
            company_elem = soup.find("h2", class_="company-card-name")
            company = company_elem.get_text(strip=True) if company_elem else ""

            # Extract location (usually worldwide)
            location = "Worldwide Remote"

            # Get all text
            raw_text = soup.get_text(separator=" ", strip=True)

            logger.info(f"Successfully scraped WeWorkRemotely job: {title}")

            return {
                "title": title,
                "company": company,
                "location": location,
                "description": raw_text,
                "raw_text": raw_text,
                "scrape_success": True
            }

        except Exception as e:
            logger.warning(f"Failed to scrape WeWorkRemotely URL {url}: {e}")
            return self._empty_result()

    async def _scrape_generic(self, url: str) -> dict:
        """Generic scraper for unknown sites."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers, follow_redirects=True)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Try to extract title from h1 or title tag
            title_elem = soup.find("h1") or soup.find("title")
            title = title_elem.get_text(strip=True) if title_elem else ""

            # Get all visible text
            raw_text = soup.get_text(separator=" ", strip=True)

            logger.info(f"Generic scrape of {url}: extracted {len(raw_text)} chars")

            return {
                "title": title,
                "company": "",
                "location": "",
                "description": raw_text,
                "raw_text": raw_text,
                "scrape_success": True
            }

        except Exception as e:
            logger.warning(f"Generic scrape failed for {url}: {e}")
            return self._empty_result()

    def _empty_result(self) -> dict:
        """Return empty result when scraping fails."""
        return {
            "title": "",
            "company": "",
            "location": "",
            "description": "",
            "raw_text": "",
            "scrape_success": False
        }
