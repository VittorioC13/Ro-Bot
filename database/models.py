"""
Database models for Robotics Daily Report System
Defines all SQLAlchemy models for PostgreSQL database
"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Date, ForeignKey, DECIMAL, JSON, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Article(Base):
    """
    Main articles table storing scraped robotics news
    """
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(String(100), nullable=False)
    author = Column(String(200))
    published_date = Column(TIMESTAMP)
    scraped_date = Column(TIMESTAMP, default=datetime.utcnow)
    excerpt = Column(Text)
    full_text = Column(Text)
    image_url = Column(String(1000))
    read_time_minutes = Column(Integer)

    # Relationships
    categories = relationship('ArticleCategory', back_populates='article', cascade='all, delete-orphan')
    summary = relationship('AISummary', back_populates='article', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        """Convert article to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'author': self.author,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'scraped_date': self.scraped_date.isoformat() if self.scraped_date else None,
            'excerpt': self.excerpt,
            'image_url': self.image_url,
            'read_time_minutes': self.read_time_minutes,
            'categories': [ac.category.name for ac in self.categories],
            'summary': self.summary.summary if self.summary else None
        }


class Category(Base):
    """
    Categories for organizing robotics articles
    """
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    icon = Column(String(50))

    # Relationships
    articles = relationship('ArticleCategory', back_populates='category')

    def to_dict(self):
        """Convert category to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'article_count': len(self.articles)
        }


class ArticleCategory(Base):
    """
    Many-to-many relationship table between articles and categories
    Includes confidence score from AI categorization
    """
    __tablename__ = 'article_categories'

    article_id = Column(Integer, ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
    confidence_score = Column(DECIMAL(3, 2))

    # Relationships
    article = relationship('Article', back_populates='categories')
    category = relationship('Category', back_populates='articles')


class AISummary(Base):
    """
    AI-generated summaries for articles using GPT-4
    """
    __tablename__ = 'ai_summaries'

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id', ondelete='CASCADE'), unique=True)
    summary = Column(Text, nullable=False)
    key_insights = Column(JSON)
    generated_date = Column(TIMESTAMP, default=datetime.utcnow)
    model_used = Column(String(50), default='gpt-4')

    # Relationships
    article = relationship('Article', back_populates='summary')

    def to_dict(self):
        """Convert summary to dictionary for API responses"""
        return {
            'id': self.id,
            'article_id': self.article_id,
            'summary': self.summary,
            'key_insights': self.key_insights,
            'generated_date': self.generated_date.isoformat() if self.generated_date else None,
            'model_used': self.model_used
        }


class TrendingTopic(Base):
    """
    Tracks trending topics, companies, and technologies in robotics
    """
    __tablename__ = 'trending_topics'

    id = Column(Integer, primary_key=True)
    topic_name = Column(String(200), nullable=False)
    mention_count = Column(Integer, default=1)
    date = Column(Date, default=datetime.utcnow().date)
    related_articles = Column(JSON)  # Store article IDs as JSON array

    def to_dict(self):
        """Convert trending topic to dictionary for API responses"""
        return {
            'id': self.id,
            'topic_name': self.topic_name,
            'mention_count': self.mention_count,
            'date': self.date.isoformat() if self.date else None,
            'related_articles': self.related_articles
        }
