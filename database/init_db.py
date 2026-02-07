"""
Database initialization script for Robotics Daily Report System
Creates all tables and inserts initial categories
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
    Initialize database by creating all tables and inserting initial data
    """
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        print("Please set DATABASE_URL in your .env file")
        return False

    try:
        # Create engine
        print(f"Connecting to database...")
        engine = create_engine(database_url)

        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(engine)
        print("✓ All tables created successfully")

        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Insert initial categories
        print("\nInserting initial categories...")
        initial_categories = [
            {
                'name': 'Humanoid Robots',
                'description': 'Human-like robots with bipedal locomotion and anthropomorphic features',
                'icon': '🤖'
            },
            {
                'name': 'Drones & Aerial Systems',
                'description': 'Unmanned aerial vehicles and flying robotics platforms',
                'icon': '🚁'
            },
            {
                'name': 'Industrial Automation',
                'description': 'Manufacturing robots, robotic arms, and factory automation systems',
                'icon': '🏭'
            },
            {
                'name': 'AGVs & AMRs',
                'description': 'Autonomous Guided Vehicles and Autonomous Mobile Robots for logistics',
                'icon': '📦'
            },
            {
                'name': 'AI & Software',
                'description': 'Artificial intelligence, machine learning, and robotics software platforms',
                'icon': '🧠'
            },
            {
                'name': 'Research & Academia',
                'description': 'Academic research, university projects, and scientific breakthroughs',
                'icon': '🔬'
            },
            {
                'name': 'Business & Funding',
                'description': 'Investment rounds, acquisitions, IPOs, and financial news',
                'icon': '💰'
            },
            {
                'name': 'Healthcare Robotics',
                'description': 'Medical robots, surgical systems, and healthcare automation',
                'icon': '⚕️'
            },
            {
                'name': 'Agricultural Robotics',
                'description': 'Farming automation, crop monitoring, and agricultural robots',
                'icon': '🌾'
            },
            {
                'name': 'Consumer Robotics',
                'description': 'Home robots, entertainment bots, and consumer-facing products',
                'icon': '🏠'
            }
        ]

        for cat_data in initial_categories:
            # Check if category already exists
            existing = session.query(Category).filter_by(name=cat_data['name']).first()
            if not existing:
                category = Category(**cat_data)
                session.add(category)
                print(f"  + Added: {cat_data['name']}")
            else:
                print(f"  - Already exists: {cat_data['name']}")

        session.commit()
        print("\n✓ Database initialization completed successfully!")

        # Display summary
        category_count = session.query(Category).count()
        print(f"\nDatabase Summary:")
        print(f"  - Categories: {category_count}")

        session.close()
        return True

    except Exception as e:
        print(f"\n✗ ERROR: Database initialization failed")
        print(f"Error details: {str(e)}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Robotics Daily Report - Database Initialization")
    print("=" * 60)
    print()

    success = init_database()

    if success:
        print("\n" + "=" * 60)
        print("Database is ready to use!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Database initialization failed. Please check the errors above.")
        print("=" * 60)
        sys.exit(1)
