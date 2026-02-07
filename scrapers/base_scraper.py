"""
Base scraper class for Robotics Daily Report System
Abstract base class with common methods for all scrapers
"""

from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for all news source scrapers
    Provides common functionality for HTTP requests, rate limiting, and error handling
    """

    def __init__(self, source_name: str, base_url: str, rate_limit_seconds: float = 1.0):
        """
        Initialize scraper

        Args:
            source_name: Name of the news source
            base_url: Base URL for the source
            rate_limit_seconds: Delay between requests in seconds
        """
        self.source_name = source_name
        self.base_url = base_url
        self.rate_limit_seconds = rate_limit_seconds
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_url(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Fetch URL content with error handling and rate limiting

        Args:
            url: URL to fetch
            timeout: Request timeout in seconds

        Returns:
            HTML content as string, or None if request failed
        """
        try:
            logger.info(f"[{self.source_name}] Fetching: {url}")
            time.sleep(self.rate_limit_seconds)  # Rate limiting

            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()

            return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"[{self.source_name}] Request failed for {url}: {str(e)}")
            return None

    def parse_html(self, html_content: str) -> Optional[BeautifulSoup]:
        """
        Parse HTML content with BeautifulSoup

        Args:
            html_content: Raw HTML string

        Returns:
            BeautifulSoup object or None if parsing failed
        """
        try:
            return BeautifulSoup(html_content, 'lxml')
        except Exception as e:
            logger.error(f"[{self.source_name}] HTML parsing failed: {str(e)}")
            return None

    def clean_text(self, text: Optional[str]) -> str:
        """
        Clean and normalize text content

        Args:
            text: Raw text string

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = ' '.join(text.split())

        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    def parse_date(self, date_str: str, formats: List[str]) -> Optional[datetime]:
        """
        Parse date string with multiple format attempts

        Args:
            date_str: Date string to parse
            formats: List of datetime format strings to try

        Returns:
            datetime object or None if parsing failed
        """
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        logger.warning(f"[{self.source_name}] Could not parse date: {date_str}")
        return None

    def estimate_read_time(self, text: str) -> int:
        """
        Estimate read time in minutes based on word count
        Assumes average reading speed of 200 words per minute

        Args:
            text: Article text content

        Returns:
            Estimated read time in minutes
        """
        if not text:
            return 0

        word_count = len(text.split())
        read_time = max(1, round(word_count / 200))
        return read_time

    @abstractmethod
    def scrape(self, max_articles: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape articles from the source
        Must be implemented by each scraper subclass

        Args:
            max_articles: Maximum number of articles to scrape

        Returns:
            List of article dictionaries with standardized fields:
            {
                'title': str,
                'url': str,
                'source': str,
                'author': str (optional),
                'published_date': datetime (optional),
                'excerpt': str (optional),
                'full_text': str (optional),
                'image_url': str (optional)
            }
        """
        pass

    def validate_article(self, article: Dict[str, Any]) -> bool:
        """
        Validate that article has required fields

        Args:
            article: Article dictionary

        Returns:
            True if valid, False otherwise
        """
        required_fields = ['title', 'url', 'source']

        for field in required_fields:
            if field not in article or not article[field]:
                logger.warning(f"[{self.source_name}] Article missing required field: {field}")
                return False

        return True

    def log_scrape_results(self, articles: List[Dict[str, Any]]):
        """
        Log scraping results summary

        Args:
            articles: List of scraped articles
        """
        logger.info(f"[{self.source_name}] Scraping complete:")
        logger.info(f"  - Total articles scraped: {len(articles)}")

        if articles:
            with_images = sum(1 for a in articles if a.get('image_url'))
            with_dates = sum(1 for a in articles if a.get('published_date'))
            with_authors = sum(1 for a in articles if a.get('author'))

            logger.info(f"  - With images: {with_images}")
            logger.info(f"  - With dates: {with_dates}")
            logger.info(f"  - With authors: {with_authors}")
