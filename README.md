# Robotics Daily Report

A comprehensive web platform that aggregates daily robotics news from major sources, uses AI to generate summaries and categorize content, and provides an interactive dashboard for exploring the latest developments in robotics.

## Features

- **Multi-Source Aggregation**: Scrapes robotics news from 5 major sources:
  - IEEE Spectrum Robotics
  - MIT News Robotics
  - NVIDIA Blog
  - TechCrunch Robotics
  - The Robot Report

- **AI-Powered Processing**:
  - DeepSeek AI generated article summaries
  - Automatic categorization into 10 robotics categories
  - Trending topic detection

- **Interactive Dashboard**:
  - Real-time search functionality
  - Category and source filtering
  - Trending topics sidebar
  - Responsive design (mobile, tablet, desktop)

- **Daily Automation**: GitHub Actions workflow runs scraper daily at 8 AM UTC

## Technology Stack

- **Backend**: Python Flask 3 (serverless on Vercel)
- **Database**: SQLite (file-based, zero setup required)
- **AI**: DeepSeek API (OpenAI-compatible)
- **Web Scraping**: BeautifulSoup4, Requests, Feedparser
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Vercel
- **Automation**: GitHub Actions

## Project Structure

```
robotics-report/
├── api/                    # Flask API endpoints
│   ├── index.py           # Main Flask app
│   ├── articles.py        # Article endpoints
│   ├── search.py          # Search endpoint
│   └── admin.py           # Admin endpoints
├── scrapers/              # Web scrapers
│   ├── base_scraper.py    # Base scraper class
│   ├── ieee_scraper.py    # IEEE Spectrum scraper
│   ├── mit_scraper.py     # MIT News scraper
│   ├── nvidia_scraper.py  # NVIDIA Blog scraper
│   ├── techcrunch_scraper.py
│   ├── robotreport_scraper.py
│   └── scraper_manager.py # Orchestrator
├── ai_processor/          # AI processing
│   ├── summarizer.py      # DeepSeek AI summaries
│   ├── categorizer.py     # Auto-categorization
│   └── trending_detector.py
├── database/              # Database layer
│   ├── models.py          # SQLAlchemy models
│   ├── init_db.py         # DB initialization
│   └── queries.py         # Common queries
├── public/                # Frontend
│   ├── index.html         # Dashboard
│   ├── styles.css         # Styling
│   └── app.js             # Frontend logic
├── .github/workflows/     # GitHub Actions
│   └── daily_scrape.yml   # Daily automation
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel config
└── .env.example          # Environment template
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- DeepSeek API key: `sk-16e2f4dcccef43d9ad17e66607bf4b82` (already configured!)
- Git

**No database setup needed!** Uses SQLite (file-based).

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/robotics-report.git
cd robotics-report
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
python database/init_sqlite.py
```

This creates `robotics.db` file and sets up all tables. That's it - no configuration needed!

### 4. Run First Scrape

```bash
python scrapers/scraper_manager.py
```

This will:
- Scrape articles from all 5 sources
- Generate AI summaries
- Auto-categorize articles
- Extract trending topics

### 5. Start Development Server

```bash
python api/index.py
```

Visit `http://localhost:5000` to see the dashboard.

## API Endpoints

### Public Endpoints

```
GET /api/articles
  Query params: page, limit, category, source, date_from, date_to
  Returns: Paginated list of articles

GET /api/articles/<id>
  Returns: Full article details

GET /api/search?q=<query>
  Returns: Search results

GET /api/categories
  Returns: List of all categories

GET /api/trending
  Query params: days, limit
  Returns: Trending topics

GET /api/sources
  Returns: List of sources with counts
```

### Admin Endpoints (require X-API-Key header)

```
POST /api/admin/scrape
  Triggers manual scrape of all sources

GET /api/admin/status
  Returns: System statistics
```

## Deployment to Vercel

### Option 1: Quick Deploy (Recommended for SQLite)

1. Push your `robotics.db` file to GitHub (after running initial scrape)
2. Go to https://vercel.com/new
3. Import `VittorioC13/Ro-Bot`
4. Add environment variable:
   - `DEEPSEEK_API_KEY` = `sk-16e2f4dcccef43d9ad17e66607bf4b82`
5. Deploy!

**Note**: SQLite on Vercel is read-only after deployment. New articles from GitHub Actions will update the file in your repo.

### Option 2: Use PostgreSQL for Production

See `VERCEL_SETUP.md` for full PostgreSQL setup (if you want writable database on Vercel).

### Set Up GitHub Actions

Add these secrets to your GitHub repository (Settings → Secrets):

- `DATABASE_URL`: Your production PostgreSQL connection string
- `DEEPSEEK_API_KEY`: Your DeepSeek API key

The workflow will automatically run daily at 8 AM UTC.

## Manual Scraping

You can trigger scraping manually in three ways:

### 1. Local Command Line

```bash
python scrapers/scraper_manager.py
```

### 2. GitHub Actions (Manual Trigger)

Go to Actions → Daily Robotics News Scrape → Run workflow

### 3. API Endpoint

```bash
curl -X POST https://your-app.vercel.app/api/admin/scrape \
  -H "X-API-Key: your-admin-api-key"
```

## Categories

The system categorizes articles into 10 categories:

1. **Humanoid Robots** 🤖 - Human-like robots with bipedal locomotion
2. **Drones & Aerial Systems** 🚁 - Unmanned aerial vehicles
3. **Industrial Automation** 🏭 - Manufacturing robots and factory automation
4. **AGVs & AMRs** 📦 - Autonomous mobile robots for logistics
5. **AI & Software** 🧠 - AI, machine learning, and robotics software
6. **Research & Academia** 🔬 - Academic research and breakthroughs
7. **Business & Funding** 💰 - Investment rounds, acquisitions, IPOs
8. **Healthcare Robotics** ⚕️ - Medical robots and surgical systems
9. **Agricultural Robotics** 🌾 - Farming automation and crop monitoring
10. **Consumer Robotics** 🏠 - Home robots and consumer products

## Customization

### Adding New News Sources

1. Create a new scraper in `scrapers/` (inherit from `BaseScraper`)
2. Implement the `scrape()` method
3. Add to `ScraperManager` in `scraper_manager.py`

### Modifying Categories

Edit categories in `database/init_db.py` and re-run initialization.

### Changing Scrape Schedule

Edit the cron expression in `.github/workflows/daily_scrape.yml`:

```yaml
schedule:
  - cron: '0 8 * * *'  # Daily at 8 AM UTC
```

## Troubleshooting

### Database Issues

SQLite database file missing:
```bash
python database/init_sqlite.py
```

### OpenAI API Errors

- Verify API key is valid
- Check you have sufficient credits
- Rate limiting: Scraper includes delays between requests

### Scraper Failing

- Websites may change HTML structure (update selectors)
- Some sources may be temporarily down
- Check logs for specific error messages

### Vercel Deployment Issues

- Ensure all secrets are configured
- Check Vercel function logs for errors
- Verify `vercel.json` routes are correct

## Cost Estimates

### DeepSeek API

- Much more affordable than OpenAI GPT-4
- ~$0.002 per article (summary + categorization)
- 100 articles/day = ~$0.20/day = ~$6/month
- DeepSeek offers competitive pricing with good quality

**Cost Optimization**:
- Cache summaries (never regenerate)
- Batch process articles
- Monitor API usage through DeepSeek dashboard

### Database (SQLite)

- **Free**: No cost, file-based storage
- **Size**: Typically 5-50MB depending on article count
- **Storage**: Stored in your GitHub repository

### Vercel Hosting

- Hobby plan: Free for personal projects
- Bandwidth: Well within free tier limits

## Future Enhancements

- [ ] User accounts and favorites
- [ ] Email digest subscriptions
- [ ] RSS feed generation
- [ ] Data visualization dashboards
- [ ] Mobile app (iOS/Android)
- [ ] Sentiment analysis
- [ ] Company/technology tracking
- [ ] Comparative analysis features

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section

## Acknowledgments

- News sources: IEEE Spectrum, MIT News, NVIDIA Blog, TechCrunch, The Robot Report
- Built with Flask, DeepSeek AI, and Vercel
- Inspired by the TMT BOT project

---

**Built with ❤️ for the robotics community**
