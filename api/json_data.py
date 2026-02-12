"""
JSON-based data loader - fallback for when SQLite doesn't work on Vercel
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Cache the loaded data
_data_cache = None


def load_data() -> Dict[str, Any]:
    """Load data from JSON file"""
    global _data_cache

    if _data_cache is not None:
        return _data_cache

    # Find the JSON file
    json_path = None
    possible_paths = [
        'data.json',
        os.path.join(os.getcwd(), 'data.json'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data.json'),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            json_path = path
            break

    if not json_path:
        return {'articles': [], 'categories': [], 'trending': [], 'sources': []}

    with open(json_path, 'r', encoding='utf-8') as f:
        _data_cache = json.load(f)

    return _data_cache


def get_articles_json(page: int = 1, limit: int = 20, category: Optional[str] = None,
                     source: Optional[str] = None) -> Dict[str, Any]:
    """Get paginated articles from JSON"""
    data = load_data()
    articles = data.get('articles', [])

    # Filter by category if specified
    if category:
        articles = [a for a in articles if category in (a.get('categories') or [])]

    # Filter by source if specified
    if source:
        articles = [a for a in articles if a.get('source') == source]

    # Paginate
    total = len(articles)
    start = (page - 1) * limit
    end = start + limit
    articles_page = articles[start:end]

    return {
        'articles': articles_page,
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': (total + limit - 1) // limit
    }


def get_categories_json() -> List[Dict[str, Any]]:
    """Get categories from JSON"""
    data = load_data()
    categories = data.get('categories', [])

    # Add article counts
    articles = data.get('articles', [])
    for cat in categories:
        cat['article_count'] = sum(1 for a in articles if cat['name'] in (a.get('categories') or []))

    return categories


def get_trending_json(days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
    """Get trending topics from JSON"""
    data = load_data()
    trending = data.get('trending', [])[:limit]
    return trending


def get_sources_json() -> List[Dict[str, Any]]:
    """Get sources from JSON"""
    data = load_data()
    return data.get('sources', [])


def search_articles_json(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Search articles from JSON"""
    data = load_data()
    articles = data.get('articles', [])

    query_lower = query.lower()

    # Search in title, excerpt, and summary
    results = []
    for article in articles:
        title = (article.get('title') or '').lower()
        excerpt = (article.get('excerpt') or '').lower()
        summary = (article.get('summary') or '').lower()

        if query_lower in title or query_lower in excerpt or query_lower in summary:
            results.append(article)

        if len(results) >= limit:
            break

    return results
