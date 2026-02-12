"""
Simple static data API that serves pre-exported JSON
No database required - works reliably on Vercel
"""

import os
import json
from flask import Blueprint, jsonify, request

data_bp = Blueprint('data', __name__)

# Load data once at module level
_data = None

def get_data():
    global _data
    if _data is not None:
        return _data

    # Try multiple paths to find data.json
    paths = [
        'data.json',
        os.path.join(os.getcwd(), 'data.json'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data.json'),
        '/var/task/data.json',  # Vercel specific path
    ]

    for path in paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                _data = json.load(f)
                return _data

    # Return empty data if file not found
    return {'articles': [], 'categories': [], 'trending': [], 'sources': []}


@data_bp.route('/data/articles', methods=['GET'])
def get_all_articles():
    """Get all articles from JSON - simple and reliable"""
    try:
        data = get_data()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))

        articles = data.get('articles', [])
        total = len(articles)
        start = (page - 1) * limit
        end = start + limit

        return jsonify({
            'success': True,
            'data': {
                'articles': articles[start:end],
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@data_bp.route('/data/categories', methods=['GET'])
def get_all_categories():
    """Get categories from JSON"""
    try:
        data = get_data()
        return jsonify({
            'success': True,
            'data': {
                'categories': data.get('categories', []),
                'total': len(data.get('categories', []))
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@data_bp.route('/data/sources', methods=['GET'])
def get_all_sources():
    """Get sources from JSON"""
    try:
        data = get_data()
        return jsonify({
            'success': True,
            'data': {
                'sources': data.get('sources', []),
                'total': len(data.get('sources', []))
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@data_bp.route('/data/trending', methods=['GET'])
def get_all_trending():
    """Get trending topics from JSON"""
    try:
        data = get_data()
        limit = int(request.args.get('limit', 10))
        trending = data.get('trending', [])[:limit]

        return jsonify({
            'success': True,
            'data': {
                'trending_topics': trending,
                'total': len(trending)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
