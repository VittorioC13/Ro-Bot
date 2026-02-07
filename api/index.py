"""
Main Flask application for Robotics Daily Report System
Entry point for Vercel serverless deployment
"""

import os
import sys
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Base
from api.articles import articles_bp
from api.search import search_bp
from api.admin import admin_bp

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Enable CORS for all routes
CORS(app)

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("WARNING: DATABASE_URL not set. Please configure your .env file.")

try:
    engine = create_engine(DATABASE_URL) if DATABASE_URL else None
    SessionLocal = scoped_session(sessionmaker(bind=engine)) if engine else None
except Exception as e:
    print(f"Database connection error: {e}")
    engine = None
    SessionLocal = None


# Dependency to get database session
def get_db():
    """Create database session for each request"""
    if not SessionLocal:
        raise Exception("Database not configured. Please set DATABASE_URL in environment variables.")
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Session cleanup handled by scoped_session


# Make get_db available to blueprints
app.get_db = get_db


# Register blueprints
app.register_blueprint(articles_bp, url_prefix='/api')
app.register_blueprint(search_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')


@app.route('/')
def index():
    """Root endpoint - API info"""
    return jsonify({
        'name': 'Robotics Daily Report API',
        'version': '1.0.0',
        'description': 'Daily aggregation of robotics news from major sources',
        'endpoints': {
            'articles': '/api/articles',
            'article_detail': '/api/articles/<id>',
            'search': '/api/search?q=<query>',
            'categories': '/api/categories',
            'trending': '/api/trending',
            'sources': '/api/sources',
            'admin_scrape': '/api/admin/scrape'
        },
        'documentation': 'https://github.com/yourusername/robotics-report',
        'status': 'operational'
    })


@app.route('/api/health')
def health():
    """Health check endpoint"""
    db_status = 'connected' if SessionLocal else 'not_configured'

    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'status': 404
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'status': 500
    }), 500


@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all other exceptions"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(error),
        'status': 500
    }), 500


# Required for Vercel deployment
if __name__ == '__main__':
    # Local development server
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)


# Vercel requires the app object to be available at module level
# This is the handler Vercel will use
handler = app
