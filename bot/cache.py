"""SQLite cache for job analysis results."""

import sqlite3
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CachedResult:
    """Cached job analysis result."""
    url: str
    verdict: str
    reason: str
    scraped_content: str
    analyzed_at: datetime
    expires_at: datetime


class JobCache:
    """Caches job analysis results in SQLite database."""

    def __init__(self, db_path: str = "job_cache.db", ttl_hours: int = 24):
        """
        Initialize the cache.

        Args:
            db_path: Path to SQLite database file
            ttl_hours: Time-to-live for cache entries in hours
        """
        self.db_path = db_path
        self.ttl_hours = ttl_hours
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_cache (
                    url_hash TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    scraped_content TEXT,
                    analyzed_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL
                )
            """)

            # Create index for faster expiration checks
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at
                ON job_cache(expires_at)
            """)

            conn.commit()
            conn.close()

            logger.info(f"Cache database initialized at {self.db_path}")

        except Exception as e:
            logger.error(f"Failed to initialize cache database: {e}")

    def _hash_url(self, url: str) -> str:
        """Generate a hash for a URL."""
        return hashlib.sha256(url.encode()).hexdigest()

    def get(self, url: str) -> Optional[CachedResult]:
        """
        Get cached result for a URL.

        Args:
            url: The job posting URL

        Returns:
            CachedResult if found and not expired, None otherwise
        """
        try:
            url_hash = self._hash_url(url)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT url, verdict, reason, scraped_content, analyzed_at, expires_at
                FROM job_cache
                WHERE url_hash = ? AND expires_at > ?
            """, (url_hash, datetime.now()))

            row = cursor.fetchone()
            conn.close()

            if row:
                logger.info(f"Cache HIT for {url}")
                return CachedResult(
                    url=row[0],
                    verdict=row[1],
                    reason=row[2],
                    scraped_content=row[3] or "",
                    analyzed_at=datetime.fromisoformat(row[4]),
                    expires_at=datetime.fromisoformat(row[5])
                )

            logger.info(f"Cache MISS for {url}")
            return None

        except Exception as e:
            logger.error(f"Error getting cached result: {e}")
            return None

    def set(self, url: str, verdict: str, reason: str, scraped_content: str = ""):
        """
        Store a result in the cache.

        Args:
            url: The job posting URL
            verdict: The analysis verdict (helpful/not_helpful/unclear)
            reason: The reason for the verdict
            scraped_content: The scraped job content (optional)
        """
        try:
            url_hash = self._hash_url(url)
            analyzed_at = datetime.now()
            expires_at = analyzed_at + timedelta(hours=self.ttl_hours)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO job_cache
                (url_hash, url, verdict, reason, scraped_content, analyzed_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (url_hash, url, verdict, reason, scraped_content, analyzed_at, expires_at))

            conn.commit()
            conn.close()

            logger.info(f"Cached result for {url}: {verdict}")

        except Exception as e:
            logger.error(f"Error caching result: {e}")

    def clear_expired(self):
        """Remove expired cache entries."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM job_cache
                WHERE expires_at <= ?
            """, (datetime.now(),))

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted_count > 0:
                logger.info(f"Cleared {deleted_count} expired cache entries")

        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")

    def clear_all(self):
        """Remove all cache entries."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM job_cache")

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            logger.info(f"Cleared all {deleted_count} cache entries")
            return deleted_count

        except Exception as e:
            logger.error(f"Error clearing all cache: {e}")
            return 0

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Total entries
            cursor.execute("SELECT COUNT(*) FROM job_cache")
            total = cursor.fetchone()[0]

            # Active (not expired) entries
            cursor.execute("SELECT COUNT(*) FROM job_cache WHERE expires_at > ?", (datetime.now(),))
            active = cursor.fetchone()[0]

            # Verdict breakdown
            cursor.execute("""
                SELECT verdict, COUNT(*)
                FROM job_cache
                WHERE expires_at > ?
                GROUP BY verdict
            """, (datetime.now(),))
            verdicts = dict(cursor.fetchall())

            conn.close()

            return {
                "total_entries": total,
                "active_entries": active,
                "expired_entries": total - active,
                "verdicts": verdicts
            }

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
