"""
Admin API endpoints for Robotics Daily Report System
Protected endpoints for administrative operations
"""

import os
import sys
from flask import Blueprint, jsonify, request
from functools import wraps

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

admin_bp = Blueprint('admin', __name__)

# Admin API key from environment
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY')


def require_api_key(f):
    """Decorator to protect endpoints with API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not ADMIN_API_KEY:
            return jsonify({
                'success': False,
                'error': 'Server configuration error',
                'message': 'Admin API key not configured'
            }), 500

        if not api_key or api_key != ADMIN_API_KEY:
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Invalid or missing API key'
            }), 401

        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route('/admin/scrape', methods=['POST'])
@require_api_key
def trigger_scrape():
    """
    POST /api/admin/scrape

    Headers:
    - X-API-Key: Admin API key (required)

    Triggers manual scrape of all sources
    Returns summary of scraping results
    """
    try:
        # Import here to avoid circular dependencies
        from scrapers.scraper_manager import ScraperManager
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            return jsonify({
                'success': False,
                'error': 'Configuration error',
                'message': 'DATABASE_URL not configured'
            }), 500

        # Create database session
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        db = Session()

        # Run scraper manager
        manager = ScraperManager(db)
        results = manager.run_all_scrapers()

        db.close()

        return jsonify({
            'success': True,
            'data': {
                'message': 'Scraping completed',
                'results': results
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Scraping failed',
            'message': str(e)
        }), 500


@admin_bp.route('/admin/status', methods=['GET'])
@require_api_key
def admin_status():
    """
    GET /api/admin/status

    Headers:
    - X-API-Key: Admin API key (required)

    Returns system status and statistics
    """
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database.models import Article, Category, AISummary, TrendingTopic
        from datetime import datetime, timedelta

        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            return jsonify({
                'success': False,
                'error': 'Configuration error',
                'message': 'DATABASE_URL not configured'
            }), 500

        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        db = Session()

        # Get statistics
        total_articles = db.query(Article).count()
        total_summaries = db.query(AISummary).count()
        total_categories = db.query(Category).count()
        total_trending = db.query(TrendingTopic).count()

        # Articles from last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        articles_24h = db.query(Article).filter(Article.scraped_date >= yesterday).count()

        db.close()

        return jsonify({
            'success': True,
            'data': {
                'status': 'operational',
                'statistics': {
                    'total_articles': total_articles,
                    'total_summaries': total_summaries,
                    'total_categories': total_categories,
                    'trending_topics': total_trending,
                    'articles_last_24h': articles_24h
                },
                'timestamp': datetime.utcnow().isoformat()
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Status check failed',
            'message': str(e)
        }), 500
