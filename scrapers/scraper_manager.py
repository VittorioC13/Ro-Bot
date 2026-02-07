"""
Scraper Manager for Robotics Daily Report System
Orchestrates all scrapers and AI processing pipeline
"""

import os
import sys
import logging
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.ieee_scraper import IEEEScraper
from scrapers.mit_scraper import MITScraper
from scrapers.nvidia_scraper import NVIDIAScraper
from scrapers.techcrunch_scraper import TechCrunchScraper
from scrapers.robotreport_scraper import RobotReportScraper
from ai_processor.summarizer import ArticleSummarizer
from ai_processor.categorizer import ArticleCategorizer
from ai_processor.trending_detector import TrendingDetector
from database.queries import (
    get_article_by_url,
    create_article,
    add_article_category,
    create_ai_summary,
    update_trending_topic
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScraperManager:
    """
    Manages all scrapers and coordinates the article processing pipeline
    """

    def __init__(self, db_session):
        """
        Initialize scraper manager

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

        # Initialize all scrapers
        self.scrapers = [
            IEEEScraper(),
            MITScraper(),
            NVIDIAScraper(),
            TechCrunchScraper(),
            RobotReportScraper()
        ]

        # Initialize AI processors
        self.summarizer = ArticleSummarizer()
        self.categorizer = ArticleCategorizer()
        self.trending_detector = TrendingDetector()

    def run_all_scrapers(self, max_articles_per_source: int = 20) -> Dict[str, Any]:
        """
        Run all scrapers and process articles

        Args:
            max_articles_per_source: Maximum articles to scrape per source

        Returns:
            Dictionary with scraping results and statistics
        """
        logger.info("=" * 60)
        logger.info("Starting Daily Robotics News Scrape")
        logger.info("=" * 60)

        start_time = datetime.now()

        results = {
            'timestamp': start_time.isoformat(),
            'sources': {},
            'total_scraped': 0,
            'total_new': 0,
            'total_duplicates': 0,
            'total_errors': 0
        }

        # Run each scraper
        for scraper in self.scrapers:
            source_name = scraper.source_name
            logger.info(f"\n{'='*60}")
            logger.info(f"Scraping: {source_name}")
            logger.info(f"{'='*60}")

            try:
                # Scrape articles
                articles = scraper.scrape(max_articles=max_articles_per_source)

                source_stats = {
                    'scraped': len(articles),
                    'new': 0,
                    'duplicates': 0,
                    'errors': 0
                }

                # Process each article
                for article_data in articles:
                    try:
                        processed = self._process_article(article_data)

                        if processed == 'new':
                            source_stats['new'] += 1
                        elif processed == 'duplicate':
                            source_stats['duplicates'] += 1
                        else:
                            source_stats['errors'] += 1

                    except Exception as e:
                        logger.error(f"Error processing article: {str(e)}")
                        source_stats['errors'] += 1

                results['sources'][source_name] = source_stats
                results['total_scraped'] += source_stats['scraped']
                results['total_new'] += source_stats['new']
                results['total_duplicates'] += source_stats['duplicates']
                results['total_errors'] += source_stats['errors']

                logger.info(f"✓ {source_name}: {source_stats['new']} new, {source_stats['duplicates']} duplicates")

            except Exception as e:
                logger.error(f"✗ {source_name} scraper failed: {str(e)}")
                results['sources'][source_name] = {'error': str(e)}

        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info(f"\n{'='*60}")
        logger.info("Scraping Complete")
        logger.info(f"{'='*60}")
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info(f"Total articles scraped: {results['total_scraped']}")
        logger.info(f"New articles added: {results['total_new']}")
        logger.info(f"Duplicates skipped: {results['total_duplicates']}")
        logger.info(f"Errors: {results['total_errors']}")
        logger.info(f"{'='*60}\n")

        results['duration_seconds'] = duration

        return results

    def _process_article(self, article_data: Dict[str, Any]) -> str:
        """
        Process a single article: check duplicates, add to DB, generate summary, categorize

        Args:
            article_data: Article dictionary from scraper

        Returns:
            'new', 'duplicate', or 'error'
        """
        url = article_data.get('url')

        if not url:
            logger.warning("Article missing URL, skipping")
            return 'error'

        # Check if article already exists
        existing = get_article_by_url(self.db, url)

        if existing:
            logger.debug(f"Duplicate article skipped: {article_data.get('title', '')[:50]}")
            return 'duplicate'

        # Create article in database
        try:
            article = create_article(self.db, article_data)
            logger.info(f"Added new article: {article.title[:60]}...")

            # Generate AI summary
            self._add_summary(article, article_data)

            # Categorize article
            self._categorize_article(article, article_data)

            # Extract trending topics
            self._extract_trending(article, article_data)

            return 'new'

        except Exception as e:
            logger.error(f"Failed to process article: {str(e)}")
            return 'error'

    def _add_summary(self, article, article_data: Dict):
        """Generate and add AI summary to article"""
        try:
            summary = self.summarizer.generate_summary(article_data)

            if summary:
                create_ai_summary(
                    self.db,
                    article_id=article.id,
                    summary=summary
                )
                logger.debug(f"  + Generated summary")

        except Exception as e:
            logger.warning(f"  - Summary generation failed: {str(e)}")

    def _categorize_article(self, article, article_data: Dict):
        """Categorize article and add to database"""
        try:
            categories = self.categorizer.categorize_article(article_data)

            for category_name, confidence in categories:
                try:
                    add_article_category(
                        self.db,
                        article_id=article.id,
                        category_name=category_name,
                        confidence_score=confidence
                    )
                except Exception as e:
                    logger.warning(f"  - Failed to add category {category_name}: {str(e)}")

            if categories:
                logger.debug(f"  + Categorized into: {[c[0] for c in categories]}")

        except Exception as e:
            logger.warning(f"  - Categorization failed: {str(e)}")

    def _extract_trending(self, article, article_data: Dict):
        """Extract and update trending topics"""
        try:
            topics = self.trending_detector.extract_topics(article_data)

            for topic in topics:
                try:
                    update_trending_topic(self.db, topic, article.id)
                except Exception as e:
                    logger.warning(f"  - Failed to update trending topic {topic}: {str(e)}")

            if topics:
                logger.debug(f"  + Extracted topics: {topics}")

        except Exception as e:
            logger.warning(f"  - Trending extraction failed: {str(e)}")


def main():
    """
    Main entry point for running scraper manager standalone
    """
    from dotenv import load_dotenv
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Load environment
    load_dotenv()

    # Get database URL
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        logger.error("DATABASE_URL not set in environment")
        return

    # Create database session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db = Session()

    # Run scraper manager
    manager = ScraperManager(db)
    results = manager.run_all_scrapers()

    db.close()

    # Print results
    print("\n" + "=" * 60)
    print("SCRAPING RESULTS")
    print("=" * 60)
    for source, stats in results['sources'].items():
        print(f"{source}: {stats}")


if __name__ == '__main__':
    main()
