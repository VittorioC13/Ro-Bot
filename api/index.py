"""
Main Flask application for Robotics Daily Report System
Entry point for Vercel serverless deployment
"""

import os
import sys
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Base
from api.articles import articles_bp
from api.search import search_bp
from api.admin import admin_bp
from api.data import data_bp

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Enable CORS for all routes
CORS(app)

# Database setup - improved for Vercel
def get_database_path():
    """Get the correct database path for current environment"""
    # First check if DATABASE_URL is set
    db_url = os.getenv('DATABASE_URL')
    if db_url and not db_url.startswith('sqlite'):
        return db_url

    # For SQLite, find the database file
    # Try current directory first
    current_dir = os.getcwd()
    db_path = os.path.join(current_dir, 'robotics.db')

    if os.path.exists(db_path):
        return f'sqlite:///{db_path}'

    # Try parent of api directory
    api_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(api_dir)
    db_path = os.path.join(project_root, 'robotics.db')

    if os.path.exists(db_path):
        return f'sqlite:///{db_path}'

    # Try relative path
    db_path = os.path.abspath('robotics.db')
    if os.path.exists(db_path):
        return f'sqlite:///{db_path}'

    # Last resort - return the path anyway
    return f'sqlite:///{db_path}'

try:
    DATABASE_URL = get_database_path()
    print(f"[INFO] Using database: {DATABASE_URL}")

    # Create engine with appropriate settings
    if DATABASE_URL.startswith('sqlite'):
        engine = create_engine(
            DATABASE_URL,
            connect_args={'check_same_thread': False},
            pool_pre_ping=True,
            echo=False
        )
    else:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    SessionLocal = scoped_session(sessionmaker(bind=engine))

    # Test the connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM articles"))
        count = result.scalar()
        print(f"[INFO] Database connected successfully. Articles: {count}")

except Exception as e:
    print(f"[ERROR] Database connection failed: {e}")
    import traceback
    traceback.print_exc()
    engine = None
    SessionLocal = None


# Dependency to get database session
def get_db():
    """Create database session for each request"""
    if not SessionLocal:
        raise Exception("Database not configured")
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
app.register_blueprint(data_bp, url_prefix='/api')  # Simple JSON endpoints


@app.route('/')
def index():
    """Root endpoint - API info"""
    return jsonify({
        'name': 'Robotics Daily Report API',
        'version': '1.0.0',
        'description': 'Daily aggregation of robotics news from major sources',
        'endpoints': {
            'health': '/api/health',
            'articles': '/api/articles',
            'article_detail': '/api/articles/<id>',
            'search': '/api/search?q=<query>',
            'categories': '/api/categories',
            'trending': '/api/trending',
            'sources': '/api/sources'
        },
        'status': 'operational'
    })


@app.route('/api/health')
def health():
    """Health check endpoint with diagnostics"""
    db_status = 'not_configured'
    article_count = 0
    db_info = {}

    try:
        if SessionLocal:
            db = SessionLocal()
            result = db.execute(text("SELECT COUNT(*) FROM articles"))
            article_count = result.scalar()
            db.close()
            db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'

    # Gather diagnostic info
    db_info = {
        'DATABASE_URL': DATABASE_URL if 'DATABASE_URL' in globals() else 'not set',
        'cwd': os.getcwd(),
        'files_in_cwd': os.listdir(os.getcwd())[:20],  # First 20 files
        'db_file_exists': os.path.exists('robotics.db'),
    }

    return jsonify({
        'status': 'healthy' if db_status == 'connected' else 'degraded',
        'database': db_status,
        'article_count': article_count,
        'diagnostics': db_info,
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
    print(f"[ERROR] Unhandled exception: {error}")
    import traceback
    traceback.print_exc()

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
handler = app
