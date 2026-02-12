"""
SQLite Database initialization script for Robotics Daily Report System
Creates database file and all tables
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Base, Category

# Load environment variables
load_dotenv()

def init_database():
    """
    Initialize SQLite database by creating all tables and inserting initial data
    """
    # Use SQLite database
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./robotics.db')

    # Convert to absolute path for SQLite
    if database_url.startswith('sqlite:///'):
        db_path = database_url.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            db_path = os.path.abspath(db_path)
            database_url = f'sqlite:///{db_path}'

    try:
        # Create engine
        print(f"Creating SQLite database at: {database_url}")
        engine = create_engine(database_url)

        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(engine)
        print("OK All tables created successfully")

        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Check if categories already exist
        existing_count = session.query(Category).count()
        if existing_count > 0:
            print(f"\nOK Database already initialized with {existing_count} categories")
            session.close()
            return True

        # Insert initial categories
        print("\nInserting initial categories...")
        initial_categories = [
            {
                'name': 'Humanoid Robots',
                'description': 'Human-like robots with bipedal locomotion and anthropomorphic features',
                'icon': ''
            },
            {
                'name': 'Drones & Aerial Systems',
                'description': 'Unmanned aerial vehicles and flying robotics platforms',
                'icon': ''
            },
            {
                'name': 'Industrial Automation',
                'description': 'Manufacturing robots, robotic arms, and factory automation systems',
                'icon': ''
            },
            {
                'name': 'AGVs & AMRs',
                'description': 'Autonomous Guided Vehicles and Autonomous Mobile Robots for logistics',
                'icon': ''
            },
            {
                'name': 'AI & Software',
                'description': 'Artificial intelligence, machine learning, and robotics software platforms',
                'icon': ''
            },
            {
                'name': 'Research & Academia',
                'description': 'Academic research, university projects, and scientific breakthroughs',
                'icon': ''
            },
            {
                'name': 'Business & Funding',
                'description': 'Investment rounds, acquisitions, IPOs, and financial news',
                'icon': ''
            },
            {
                'name': 'Healthcare Robotics',
                'description': 'Medical robots, surgical systems, and healthcare automation',
                'icon': ''
            },
            {
                'name': 'Agricultural Robotics',
                'description': 'Farming automation, crop monitoring, and agricultural robots',
                'icon': ''
            },
            {
                'name': 'Consumer Robotics',
                'description': 'Home robots, entertainment bots, and consumer-facing products',
                'icon': ''
            }
        ]

        for cat_data in initial_categories:
            category = Category(**cat_data)
            session.add(category)
            print(f"  + Added: {cat_data['name']}")

        session.commit()
        print("\nOK Database initialization completed successfully!")

        # Display summary
        category_count = session.query(Category).count()
        print(f"\nDatabase Summary:")
        print(f"  - Categories: {category_count}")
        print(f"  - Database file: {db_path if 'db_path' in locals() else 'robotics.db'}")

        session.close()
        return True

    except Exception as e:
        print(f"\nERROR ERROR: Database initialization failed")
        print(f"Error details: {str(e)}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Robotics Daily Report - SQLite Database Initialization")
    print("=" * 60)
    print()

    success = init_database()

    if success:
        print("\n" + "=" * 60)
        print("Database is ready to use!")
        print("You can now run: python scrapers/scraper_manager.py")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Database initialization failed. Please check the errors above.")
        print("=" * 60)
        sys.exit(1)
