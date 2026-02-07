"""
The Robot Report scraper
Scrapes https://www.therobotreport.com/
Uses HTML parsing with BeautifulSoup
"""

from datetime import datetime
from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, logger


class RobotReportScraper(BaseScraper):
    """Scraper for The Robot Report"""

    def __init__(self):
        super().__init__(
            source_name='The Robot Report',
            base_url='https://www.therobotreport.com',
            rate_limit_seconds=1.0
        )
        self.main_url = 'https://www.therobotreport.com/'

    def scrape(self, max_articles: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape articles from The Robot Report

        Args:
            max_articles: Maximum number of articles to scrape

        Returns:
            List of article dictionaries
        """
        logger.info(f"[{self.source_name}] Starting scrape...")

        articles = []

        try:
            # Fetch main page
            html_content = self.fetch_url(self.main_url)

            if not html_content:
                logger.error(f"[{self.source_name}] Failed to fetch main page")
                return articles

            soup = self.parse_html(html_content)

            if not soup:
                logger.error(f"[{self.source_name}] Failed to parse HTML")
                return articles

            # Find article cards (Robot Report uses various structures)
            article_cards = soup.find_all('article') or soup.find_all('div', class_=['post', 'entry', 'item'])

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
        title_elem = card.find(['h1', 'h2', 'h3'])
        if not title_elem:
            title_elem = card.find(class_=['title', 'entry-title', 'post-title'])

        title = self.clean_text(title_elem.get_text()) if title_elem else ''

        # Extract URL
        url = ''
        if title_elem:
            link_elem = title_elem.find('a', href=True)
            if link_elem:
                url = link_elem['href']

        if not url:
            link_elem = card.find('a', href=True)
            if link_elem:
                url = link_elem['href']

        # Make URL absolute if relative
        if url and url.startswith('/'):
            url = self.base_url + url

        # Extract excerpt/description
        excerpt_elem = card.find(class_=['excerpt', 'summary', 'entry-content'])
        if not excerpt_elem:
            # Try to find first paragraph that's not part of meta info
            for p in card.find_all('p'):
                if p.get_text().strip():
                    excerpt_elem = p
                    break

        excerpt = self.clean_text(excerpt_elem.get_text()) if excerpt_elem else ''

        # Extract image
        image_url = None
        img_elem = card.find('img', src=True)
        if img_elem:
            image_url = img_elem.get('src') or img_elem.get('data-src')
            if image_url:
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url
                elif image_url.startswith('/'):
                    image_url = self.base_url + image_url

        # Extract author
        author = None
        author_elem = card.find(class_=['author', 'byline', 'post-author']) or card.find('a', rel='author')
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
            # Look for date in common classes
            date_elem = card.find(class_=['date', 'published', 'post-date', 'entry-date'])
            if date_elem:
                date_str = self.clean_text(date_elem.get_text())
                formats = ['%B %d, %Y', '%b %d, %Y', '%Y-%m-%d', '%m/%d/%Y']
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
