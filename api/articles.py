"""
Articles API endpoints for Robotics Daily Report System
Handles article retrieval, filtering, and pagination
"""

import os
import sys
from flask import Blueprint, jsonify, request, current_app
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.queries import (
    get_articles_paginated,
    get_article_by_id,
    get_all_categories,
    get_trending_topics,
    get_sources_summary
)

articles_bp = Blueprint('articles', __name__)


@articles_bp.route('/articles', methods=['GET'])
def get_articles():
    """
    GET /api/articles

    Query parameters:
    - page: Page number (default: 1)
    - limit: Articles per page (default: 20, max: 100)
    - category: Filter by category name
    - source: Filter by source name
    - date_from: Filter from date (ISO format: YYYY-MM-DD)
    - date_to: Filter to date (ISO format: YYYY-MM-DD)

    Returns paginated list of articles with summaries
    """
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)  # Max 100 per page
        category = request.args.get('category')
        source = request.args.get('source')
        date_from_str = request.args.get('date_from')
        date_to_str = request.args.get('date_to')

        # Parse dates if provided
        date_from = datetime.fromisoformat(date_from_str) if date_from_str else None
        date_to = datetime.fromisoformat(date_to_str) if date_to_str else None

        # Get database session
        db = current_app.get_db()

        # Get articles
        result = get_articles_paginated(
            session=db,
            page=page,
            limit=limit,
            category=category,
            source=source,
            date_from=date_from,
            date_to=date_to
        )

        return jsonify({
            'success': True,
            'data': result
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid parameter value',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500
    finally:
        if 'db' in locals():
            db.close()


@articles_bp.route('/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """
    GET /api/articles/<id>

    Returns full article details with AI summary
    """
    try:
        db = current_app.get_db()

        article = get_article_by_id(db, article_id)

        if not article:
            return jsonify({
                'success': False,
                'error': 'Not found',
                'message': f'Article with ID {article_id} not found'
            }), 404

        return jsonify({
            'success': True,
            'data': article.to_dict()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500
    finally:
        if 'db' in locals():
            db.close()


@articles_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    GET /api/categories

    Returns list of all categories with article counts
    """
    try:
        db = current_app.get_db()

        categories = get_all_categories(db)

        return jsonify({
            'success': True,
            'data': {
                'categories': [cat.to_dict() for cat in categories],
                'total': len(categories)
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500
    finally:
        if 'db' in locals():
            db.close()


@articles_bp.route('/trending', methods=['GET'])
def get_trending():
    """
    GET /api/trending

    Query parameters:
    - days: Number of days to look back (default: 7)
    - limit: Max topics to return (default: 10)

    Returns top trending topics
    """
    try:
        days = int(request.args.get('days', 7))
        limit = int(request.args.get('limit', 10))

        db = current_app.get_db()

        topics = get_trending_topics(db, days=days, limit=limit)

        return jsonify({
            'success': True,
            'data': {
                'trending_topics': [topic.to_dict() for topic in topics],
                'days': days,
                'total': len(topics)
            }
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid parameter value',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500
    finally:
        if 'db' in locals():
            db.close()


@articles_bp.route('/sources', methods=['GET'])
def get_sources():
    """
    GET /api/sources

    Returns list of all sources with article counts
    """
    try:
        db = current_app.get_db()

        sources = get_sources_summary(db)

        return jsonify({
            'success': True,
            'data': {
                'sources': sources,
                'total': len(sources)
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500
    finally:
        if 'db' in locals():
            db.close()
