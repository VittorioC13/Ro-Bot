"""
NVIDIA Robotics Blog scraper
Scrapes https://blogs.nvidia.com/blog/category/robotics/
Uses HTML parsing with BeautifulSoup
"""

from datetime import datetime
from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, logger


class NVIDIAScraper(BaseScraper):
    """Scraper for NVIDIA Robotics Blog"""

    def __init__(self):
        super().__init__(
            source_name='NVIDIA Blog',
            base_url='https://blogs.nvidia.com',
            rate_limit_seconds=1.0
        )
        self.robotics_url = 'https://blogs.nvidia.com/blog/category/robotics/'

    def scrape(self, max_articles: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape articles from NVIDIA Robotics Blog

        Args:
            max_articles: Maximum number of articles to scrape

        Returns:
            List of article dictionaries
        """
        logger.info(f"[{self.source_name}] Starting scrape...")

        articles = []

        try:
            # Fetch main page
            html_content = self.fetch_url(self.robotics_url)

            if not html_content:
                logger.error(f"[{self.source_name}] Failed to fetch main page")
                return articles

            soup = self.parse_html(html_content)

            if not soup:
                logger.error(f"[{self.source_name}] Failed to parse HTML")
                return articles

            # Find article cards
            # NVIDIA uses various article card structures - try common patterns
            article_cards = soup.find_all('article') or soup.find_all('div', class_=['post', 'entry', 'card'])

            if not article_cards:
                logger.warning(f"[{self.source_name}] No article cards found")
                return articles

            # Parse each article card
            for card in article_cards[:max_articles]:
                try:
                    article = self._parse_article_card(card)

                    if article and self.validate_article(article):
                        articles.append(article)

                except Exception as e:
                    logger.error(f"[{self.source_name}] Error parsing article card: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"[{self.source_name}] Scraping failed: {str(e)}")

        self.log_scrape_results(articles)
        return articles

    def _parse_article_card(self, card) -> Dict[str, Any]:
        """
        Parse single article card into article dictionary

        Args:
            card: BeautifulSoup element containing article data

        Returns:
            Article dictionary
        """
        # Extract title
        title_elem = (card.find('h2') or card.find('h3') or
                     card.find(class_=['title', 'entry-title', 'post-title']))
        title = self.clean_text(title_elem.get_text()) if title_elem else ''

        # Extract URL
        link_elem = card.find('a', href=True)
        url = ''
        if link_elem:
            url = link_elem['href']
            if url.startswith('/'):
                url = self.base_url + url

        # Extract excerpt/description
        excerpt_elem = (card.find('p') or card.find(class_=['excerpt', 'summary', 'description']))
        excerpt = self.clean_text(excerpt_elem.get_text()) if excerpt_elem else ''

        # Extract image
        image_url = None
        img_elem = card.find('img', src=True)
        if img_elem:
            image_url = img_elem['src']
            if image_url.startswith('/'):
                image_url = self.base_url + image_url

        # Extract date (NVIDIA sometimes doesn't show dates on listing page)
        published_date = None
        date_elem = card.find('time') or card.find(class_=['date', 'published', 'post-date'])
        if date_elem:
            date_str = date_elem.get('datetime') or date_elem.get_text()
            # Try parsing common date formats
            formats = ['%Y-%m-%d', '%B %d, %Y', '%b %d, %Y', '%Y-%m-%dT%H:%M:%S']
            published_date = self.parse_date(self.clean_text(date_str), formats)

        article = {
            'title': title,
            'url': url,
            'source': self.source_name,
            'author': None,  # Not typically shown on listing page
            'published_date': published_date,
            'excerpt': excerpt,
            'image_url': image_url,
            'full_text': None
        }

        return article
