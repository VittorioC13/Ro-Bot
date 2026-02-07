"""
TechCrunch Robotics scraper
Scrapes https://techcrunch.com/category/robotics/
Uses HTML parsing with BeautifulSoup
"""

from datetime import datetime
from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, logger


class TechCrunchScraper(BaseScraper):
    """Scraper for TechCrunch Robotics category"""

    def __init__(self):
        super().__init__(
            source_name='TechCrunch',
            base_url='https://techcrunch.com',
            rate_limit_seconds=1.0
        )
        self.robotics_url = 'https://techcrunch.com/category/robotics/'

    def scrape(self, max_articles: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape articles from TechCrunch Robotics category

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

            # TechCrunch uses post-block or article elements
            article_cards = soup.find_all(['article', 'div'], class_=lambda x: x and ('post-block' in x or 'wp-block-post' in x))

            if not article_cards:
                # Fallback to finding all article tags
                article_cards = soup.find_all('article')

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
                     card.find(class_=['post-block__title', 'post__title']))

        # If title has a link, use the link's text
        if title_elem:
            title_link = title_elem.find('a')
            title = self.clean_text(title_link.get_text() if title_link else title_elem.get_text())
        else:
            title = ''

        # Extract URL
        url = ''
        link_elem = card.find('a', href=True)
        if link_elem:
            url = link_elem['href']
            if url.startswith('/'):
                url = self.base_url + url

        # Extract excerpt/description
        excerpt_elem = card.find(class_=['post-block__content', 'excerpt'])
        if not excerpt_elem:
            excerpt_elem = card.find('p')
        excerpt = self.clean_text(excerpt_elem.get_text()) if excerpt_elem else ''

        # Extract image
        image_url = None
        img_elem = card.find('img', src=True)
        if img_elem:
            # TechCrunch might use srcset or src
            image_url = img_elem.get('src') or img_elem.get('data-src')
            if image_url and image_url.startswith('//'):
                image_url = 'https:' + image_url

        # Extract author
        author = None
        author_elem = card.find(class_=['post-block__author', 'author', 'byline'])
        if author_elem:
            author = self.clean_text(author_elem.get_text())

        # Extract date
        published_date = None
        time_elem = card.find('time', datetime=True)
        if time_elem:
            date_str = time_elem.get('datetime')
            formats = ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']
            published_date = self.parse_date(date_str, formats)
        else:
            # Look for date in text
            date_elem = card.find(class_=['date', 'published'])
            if date_elem:
                date_str = self.clean_text(date_elem.get_text())
                formats = ['%B %d, %Y', '%b %d, %Y', '%Y-%m-%d']
                published_date = self.parse_date(date_str, formats)

        article = {
            'title': title,
            'url': url,
            'source': self.source_name,
            'author': author,
            'published_date': published_date,
            'excerpt': excerpt,
            'image_url': image_url,
            'full_text': None
        }

        return article
