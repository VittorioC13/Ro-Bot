"""
Search API endpoint for Robotics Daily Report System
Handles full-text search across articles
"""

import os
import sys
from flask import Blueprint, jsonify, request, current_app

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.queries import search_articles

# Fallback JSON data loader
try:
    from api.json_data import search_articles_json
    JSON_FALLBACK_AVAILABLE = True
except ImportError:
    JSON_FALLBACK_AVAILABLE = False

search_bp = Blueprint('search', __name__)


@search_bp.route('/search', methods=['GET'])
def search():
    """
    GET /api/search?q=<query>

    Query parameters:
    - q: Search query (required)
    - limit: Max results to return (default: 50, max: 100)

    Searches across article titles, excerpts, and AI summaries
    Returns matching articles sorted by publication date
    """
    try:
        query = request.args.get('q')

        if not query:
            return jsonify({
                'success': False,
                'error': 'Missing query parameter',
                'message': 'Please provide a search query using the "q" parameter'
            }), 400

        if len(query) < 2:
            return jsonify({
                'success': False,
                'error': 'Query too short',
                'message': 'Search query must be at least 2 characters long'
            }), 400

        limit = min(int(request.args.get('limit', 50)), 100)

        # Try database first
        try:
            db = current_app.get_db()
            articles = search_articles(db, query, limit=limit)
            results = [article.to_dict() for article in articles]
            db.close()
        except Exception as db_error:
            # Fallback to JSON
            if JSON_FALLBACK_AVAILABLE:
                results = search_articles_json(query, limit=limit)
            else:
                raise db_error

        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'results': results,
                'count': len(results),
                'limit': limit
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
