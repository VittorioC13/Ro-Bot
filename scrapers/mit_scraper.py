"""
MIT News Robotics scraper
Scrapes https://news.mit.edu/topic/robotics
Uses RSS feed for efficient parsing
"""

import feedparser
from datetime import datetime
from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, logger


class MITScraper(BaseScraper):
    """Scraper for MIT News Robotics section"""

    def __init__(self):
        super().__init__(
            source_name='MIT News',
            base_url='https://news.mit.edu',
            rate_limit_seconds=0.5
        )
        self.rss_url = 'https://news.mit.edu/rss/topic/robotics'

    def scrape(self, max_articles: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape articles from MIT News RSS feed

        Args:
            max_articles: Maximum number of articles to scrape

        Returns:
            List of article dictionaries
        """
        logger.info(f"[{self.source_name}] Starting scrape...")

        articles = []

        try:
            # Parse RSS feed
            feed = feedparser.parse(self.rss_url)

            if not feed.entries:
                logger.warning(f"[{self.source_name}] No articles found in RSS feed")
                return articles

            # Process each entry
            for entry in feed.entries[:max_articles]:
                try:
                    article = self._parse_entry(entry)

                    if article and self.validate_article(article):
                        articles.append(article)

                except Exception as e:
                    logger.error(f"[{self.source_name}] Error parsing entry: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"[{self.source_name}] RSS feed parsing failed: {str(e)}")

        self.log_scrape_results(articles)
        return articles

    def _parse_entry(self, entry) -> Dict[str, Any]:
        """
        Parse single RSS entry into article dictionary

        Args:
            entry: Feedparser entry object

        Returns:
            Article dictionary
        """
        # Extract title
        title = self.clean_text(entry.get('title', ''))

        # Extract URL
        url = entry.get('link', '')

        # Extract description/excerpt
        excerpt = self.clean_text(entry.get('summary', ''))

        # Extract published date
        published_date = None
        if 'published_parsed' in entry and entry.published_parsed:
            published_date = datetime(*entry.published_parsed[:6])

        # Extract image
        image_url = None
        if 'media_content' in entry and entry.media_content:
            image_url = entry.media_content[0].get('url')
        elif 'enclosures' in entry and entry.enclosures:
            for enclosure in entry.enclosures:
                if enclosure.get('type', '').startswith('image/'):
                    image_url = enclosure.get('href')
                    break

        article = {
            'title': title,
            'url': url,
            'source': self.source_name,
            'author': None,  # MIT RSS doesn't typically include author
            'published_date': published_date,
            'excerpt': excerpt,
            'image_url': image_url,
            'full_text': None
        }

        return article
