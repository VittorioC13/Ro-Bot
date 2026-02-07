"""
Common database query operations for Robotics Daily Report System
Helper functions for frequently used database operations
"""

from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import Session
from database.models import Article, Category, ArticleCategory, AISummary, TrendingTopic
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any


def get_articles_paginated(
    session: Session,
    page: int = 1,
    limit: int = 20,
    category: Optional[str] = None,
    source: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Get paginated list of articles with optional filters

    Args:
        session: SQLAlchemy session
        page: Page number (1-indexed)
        limit: Articles per page
        category: Filter by category name
        source: Filter by source name
        date_from: Filter articles from this date
        date_to: Filter articles until this date

    Returns:
        Dictionary with articles, total count, and pagination info
    """
    query = session.query(Article)

    # Apply filters
    if category:
        query = query.join(ArticleCategory).join(Category).filter(Category.name == category)

    if source:
        query = query.filter(Article.source == source)

    if date_from:
        query = query.filter(Article.published_date >= date_from)

    if date_to:
        query = query.filter(Article.published_date <= date_to)

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    articles = query.order_by(desc(Article.published_date)).offset((page - 1) * limit).limit(limit).all()

    return {
        'articles': [article.to_dict() for article in articles],
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': (total + limit - 1) // limit
    }


def get_article_by_id(session: Session, article_id: int) -> Optional[Article]:
    """Get single article by ID"""
    return session.query(Article).filter(Article.id == article_id).first()


def get_article_by_url(session: Session, url: str) -> Optional[Article]:
    """Get article by URL (for duplicate detection)"""
    return session.query(Article).filter(Article.url == url).first()


def create_article(session: Session, article_data: Dict[str, Any]) -> Article:
    """
    Create new article in database

    Args:
        session: SQLAlchemy session
        article_data: Dictionary with article fields

    Returns:
        Created Article object
    """
    article = Article(**article_data)
    session.add(article)
    session.commit()
    session.refresh(article)
    return article


def search_articles(session: Session, query: str, limit: int = 50) -> List[Article]:
    """
    Search articles by text in title, excerpt, or summary

    Args:
        session: SQLAlchemy session
        query: Search query string
        limit: Maximum results to return

    Returns:
        List of matching Article objects
    """
    search_pattern = f"%{query}%"

    articles = session.query(Article).outerjoin(AISummary).filter(
        or_(
            Article.title.ilike(search_pattern),
            Article.excerpt.ilike(search_pattern),
            AISummary.summary.ilike(search_pattern)
        )
    ).order_by(desc(Article.published_date)).limit(limit).all()

    return articles


def get_all_categories(session: Session) -> List[Category]:
    """Get all categories with article counts"""
    return session.query(Category).all()


def get_category_by_name(session: Session, name: str) -> Optional[Category]:
    """Get category by name"""
    return session.query(Category).filter(Category.name == name).first()


def add_article_category(
    session: Session,
    article_id: int,
    category_name: str,
    confidence_score: Optional[float] = None
) -> ArticleCategory:
    """
    Associate article with a category

    Args:
        session: SQLAlchemy session
        article_id: Article ID
        category_name: Category name
        confidence_score: AI confidence score (0.0-1.0)

    Returns:
        Created ArticleCategory object
    """
    category = get_category_by_name(session, category_name)

    if not category:
        raise ValueError(f"Category '{category_name}' not found")

    article_category = ArticleCategory(
        article_id=article_id,
        category_id=category.id,
        confidence_score=confidence_score
    )

    session.add(article_category)
    session.commit()
    return article_category


def create_ai_summary(
    session: Session,
    article_id: int,
    summary: str,
    key_insights: Optional[Dict] = None,
    model_used: str = 'gpt-4'
) -> AISummary:
    """
    Create AI summary for an article

    Args:
        session: SQLAlchemy session
        article_id: Article ID
        summary: Generated summary text
        key_insights: Dictionary of key insights
        model_used: AI model name

    Returns:
        Created AISummary object
    """
    ai_summary = AISummary(
        article_id=article_id,
        summary=summary,
        key_insights=key_insights,
        model_used=model_used
    )

    session.add(ai_summary)
    session.commit()
    session.refresh(ai_summary)
    return ai_summary


def get_trending_topics(session: Session, days: int = 7, limit: int = 10) -> List[TrendingTopic]:
    """
    Get trending topics from the last N days

    Args:
        session: SQLAlchemy session
        days: Number of days to look back
        limit: Maximum topics to return

    Returns:
        List of TrendingTopic objects sorted by mention count
    """
    cutoff_date = datetime.utcnow().date() - timedelta(days=days)

    topics = session.query(TrendingTopic).filter(
        TrendingTopic.date >= cutoff_date
    ).order_by(desc(TrendingTopic.mention_count)).limit(limit).all()

    return topics


def update_trending_topic(session: Session, topic_name: str, article_id: int):
    """
    Update or create trending topic mention

    Args:
        session: SQLAlchemy session
        topic_name: Name of the topic/company/technology
        article_id: ID of article mentioning the topic
    """
    today = datetime.utcnow().date()

    # Check if topic exists for today
    topic = session.query(TrendingTopic).filter(
        and_(
            TrendingTopic.topic_name == topic_name,
            TrendingTopic.date == today
        )
    ).first()

    if topic:
        # Update existing topic
        topic.mention_count += 1
        if topic.related_articles:
            if article_id not in topic.related_articles:
                topic.related_articles.append(article_id)
        else:
            topic.related_articles = [article_id]
    else:
        # Create new topic
        topic = TrendingTopic(
            topic_name=topic_name,
            mention_count=1,
            date=today,
            related_articles=[article_id]
        )
        session.add(topic)

    session.commit()


def get_sources_summary(session: Session) -> List[Dict[str, Any]]:
    """
    Get summary of all sources with article counts

    Returns:
        List of dictionaries with source name and article count
    """
    sources = session.query(
        Article.source,
        func.count(Article.id).label('article_count')
    ).group_by(Article.source).all()

    return [{'source': source, 'article_count': count} for source, count in sources]


def delete_old_articles(session: Session, days: int = 90) -> int:
    """
    Delete articles older than specified days (cleanup utility)

    Args:
        session: SQLAlchemy session
        days: Delete articles older than this many days

    Returns:
        Number of articles deleted
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    deleted_count = session.query(Article).filter(
        Article.scraped_date < cutoff_date
    ).delete()

    session.commit()
    return deleted_count
