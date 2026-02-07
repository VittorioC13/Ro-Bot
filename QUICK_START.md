# Quick Start Guide - No Database Setup Required!

Your Robotics Daily Report uses **SQLite** - a simple file-based database that requires **zero configuration**!

## 🚀 Get Started in 3 Minutes

### Step 1: Install Dependencies

```bash
cd robotics-report
pip install -r requirements.txt
```

### Step 2: Initialize Database (One Time Only)

```bash
python database/init_sqlite.py
```

This creates a `robotics.db` file in your project folder. That's it!

### Step 3: Run Your First Scrape

```bash
python scrapers/scraper_manager.py
```

This will:
- Scrape robotics news from 5 major sources
- Generate AI summaries using DeepSeek
- Auto-categorize all articles
- Extract trending topics

Takes about 5-10 minutes to complete.

### Step 4: Start the Web Server

```bash
python api/index.py
```

Open your browser to: **http://localhost:5000**

🎉 **Done!** You'll see your robotics news dashboard!

## Daily Automation

The GitHub Action is already set up to run daily at 8 AM UTC.

Just add one secret to your GitHub repo:
- Go to: https://github.com/VittorioC13/Ro-Bot/settings/secrets/actions
- Add: `DEEPSEEK_API_KEY` = `sk-16e2f4dcccef43d9ad17e66607bf4b82`

The database file (`robotics.db`) will be stored in your repo (it's small, usually under 10MB).

## Commands Reference

```bash
# Initialize database (first time only)
python database/init_sqlite.py

# Run scrapers manually
python scrapers/scraper_manager.py

# Start web server
python api/index.py

# View database stats
python -c "from database.models import *; from sqlalchemy import create_engine; from sqlalchemy.orm import sessionmaker; engine = create_engine('sqlite:///./robotics.db'); Session = sessionmaker(bind=engine); s = Session(); print(f'Articles: {s.query(Article).count()}'); print(f'Categories: {s.query(Category).count()}')"
```

## Troubleshooting

**Issue**: ModuleNotFoundError
- **Solution**: Run `pip install -r requirements.txt`

**Issue**: Database file not found
- **Solution**: Run `python database/init_sqlite.py`

**Issue**: No articles appearing
- **Solution**: Run `python scrapers/scraper_manager.py`

## File Locations

- **Database**: `robotics.db` (auto-created in project root)
- **Logs**: Check console output
- **Config**: `.env` file

## What's Next?

1. ✅ Customize categories in `database/init_sqlite.py`
2. ✅ Add more news sources in `scrapers/`
3. ✅ Customize the frontend in `public/`
4. ✅ Deploy to Vercel (see VERCEL_SETUP.md)

That's it! No PostgreSQL, no cloud database, no complex setup. Just Python and SQLite. 🎉
