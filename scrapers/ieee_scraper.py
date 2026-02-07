"""
IEEE Spectrum Robotics scraper
Scrapes https://spectrum.ieee.org/topic/robotics/
Uses RSS feed for efficient parsing
"""

import feedparser
from datetime import datetime
from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, logger


class IEEEScraper(BaseScraper):
    """Scraper for IEEE Spectrum Robotics section"""

    def __init__(self):
        super().__init__(
            source_name='IEEE Spectrum',
            base_url='https://spectrum.ieee.org',
            rate_limit_seconds=0.5
        )
        self.rss_url = 'https://spectrum.ieee.org/feeds/topic/robotics.rss'

    def scrape(self, max_articles: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape articles from IEEE Spectrum RSS feed

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

        # Extract author
        author = None
        if 'author' in entry:
            author = entry.get('author')
        elif 'authors' in entry and entry.authors:
            author = entry.authors[0].get('name')

        # Extract published date
        published_date = None
        if 'published_parsed' in entry and entry.published_parsed:
            published_date = datetime(*entry.published_parsed[:6])

        # Extract image (IEEE uses media:thumbnail or media:content)
        image_url = None
        if 'media_thumbnail' in entry and entry.media_thumbnail:
            image_url = entry.media_thumbnail[0].get('url')
        elif 'media_content' in entry and entry.media_content:
            image_url = entry.media_content[0].get('url')

        article = {
            'title': title,
            'url': url,
            'source': self.source_name,
            'author': author,
            'published_date': published_date,
            'excerpt': excerpt,
            'image_url': image_url,
            'full_text': None  # Would need to fetch full article page
        }

        return article
