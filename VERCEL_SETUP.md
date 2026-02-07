# Vercel Deployment Guide for Robotics Daily Report

This guide will walk you through deploying your Robotics Daily Report system to Vercel.

## Prerequisites

- GitHub repository pushed (✓ Already done!)
- Vercel account (sign up at https://vercel.com)
- PostgreSQL database (we'll set this up)
- DeepSeek API key: `z5ajcjwbOd8DAjpat2YPh5PzKv84IvRk` (✓ Already configured)

## Step 1: Set Up PostgreSQL Database

You have three free options:

### Option A: Vercel Postgres (Recommended)

1. Go to https://vercel.com/dashboard
2. Click "Storage" in the top menu
3. Click "Create Database"
4. Select "Postgres"
5. Choose a name like "robotics-db"
6. Select your region
7. Click "Create"
8. Copy the connection string (starts with `postgresql://`)

### Option B: Neon (Alternative)

1. Go to https://neon.tech
2. Sign up for free account
3. Create a new project called "robotics-report"
4. Copy the connection string from the dashboard

### Option C: Supabase (Alternative)

1. Go to https://supabase.com
2. Create new project
3. Go to Settings → Database
4. Copy the connection string (use "Connection pooling" version)

## Step 2: Deploy to Vercel

### Using Vercel Dashboard (Easiest)

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your GitHub repository: `VittorioC13/Ro-Bot`
4. Click "Import"
5. Configure project:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as is)
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty

6. **Add Environment Variables** (click "Environment Variables" dropdown):

   Add these three variables:

   ```
   DATABASE_URL = [paste your PostgreSQL connection string]
   DEEPSEEK_API_KEY = z5ajcjwbOd8DAjpat2YPh5PzKv84IvRk
   ADMIN_API_KEY = ro-bot-admin-345
   ```

7. Click **"Deploy"**

8. Wait 2-3 minutes for deployment to complete

### Using Vercel CLI (Alternative)

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Navigate to project
cd robotics-report

# Deploy
vercel --prod

# Add environment variables (run these one by one)
vercel env add DATABASE_URL
# Paste your database URL when prompted

vercel env add DEEPSEEK_API_KEY
# Paste: z5ajcjwbOd8DAjpat2YPh5PzKv84IvRk

vercel env add ADMIN_API_KEY
# Type: ro-bot-admin-345
```

## Step 3: Initialize Production Database

After deployment, you need to create the database tables:

1. Copy your production DATABASE_URL from Vercel dashboard
2. On your local machine, create a temporary `.env.prod` file:

```bash
DATABASE_URL=postgresql://[your-production-url]
```

3. Run the database initialization:

```bash
python database/init_db.py
```

This creates all tables and inserts the 10 robotics categories.

## Step 4: Set Up GitHub Secrets for Daily Automation

1. Go to your GitHub repository: https://github.com/VittorioC13/Ro-Bot
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add these two secrets:

   **Secret 1:**
   - Name: `DATABASE_URL`
   - Value: [Your production PostgreSQL connection string]

   **Secret 2:**
   - Name: `DEEPSEEK_API_KEY`
   - Value: `z5ajcjwbOd8DAjpat2YPh5PzKv84IvRk`

5. GitHub Actions will now run daily at 8 AM UTC to scrape news

## Step 5: Test Your Deployment

### Test the Website

1. Open your Vercel deployment URL (e.g., `https://ro-bot-xxxxx.vercel.app`)
2. You should see the dashboard (will be empty initially)

### Run First Scrape (Manually)

Option A: Trigger via API

```bash
curl -X POST https://your-app.vercel.app/api/admin/scrape \
  -H "X-API-Key: ro-bot-admin-345"
```

Option B: Manually trigger GitHub Action

1. Go to your GitHub repo
2. Click **Actions** tab
3. Click **"Daily Robotics News Scrape"**
4. Click **"Run workflow"** button
5. Click green **"Run workflow"** button
6. Wait 5-10 minutes for completion

### Verify It Worked

1. Refresh your Vercel website
2. You should now see robotics articles!
3. Try filtering by category
4. Test the search functionality

## Step 6: Monitor Your Deployment

### View Logs

**Vercel Function Logs:**
1. Go to Vercel dashboard
2. Select your project
3. Click "Logs" tab
4. Filter by function name to see API requests

**GitHub Actions Logs:**
1. Go to your GitHub repo
2. Click "Actions" tab
3. Click on any workflow run
4. View detailed logs for each step

### Check Database

If using Vercel Postgres:
1. Go to Vercel dashboard
2. Click "Storage"
3. Select your database
4. Click "Data" tab to browse tables

## Troubleshooting

### Issue: Deployment Failed

**Solution:**
- Check the Vercel build logs for specific errors
- Ensure all environment variables are set correctly
- Verify Python version is 3.11 (Vercel default)

### Issue: Database Connection Failed

**Solution:**
- Verify DATABASE_URL is correct
- Check if database allows connections from Vercel IPs
- For Neon/Supabase, ensure connection pooling is enabled

### Issue: No Articles Appearing

**Solution:**
- Verify you ran the database initialization
- Check GitHub Actions logs to see if scraper ran successfully
- Manually trigger scrape via admin API endpoint

### Issue: AI Summaries Not Generating

**Solution:**
- Verify DEEPSEEK_API_KEY is set correctly
- Check DeepSeek API dashboard for usage/errors
- Review Vercel function logs for specific error messages

## Your Deployment URLs

After deployment, save these URLs:

- **Website**: `https://[your-project].vercel.app`
- **API Health**: `https://[your-project].vercel.app/api/health`
- **Articles API**: `https://[your-project].vercel.app/api/articles`
- **Admin Scrape**: `https://[your-project].vercel.app/api/admin/scrape`

## Cost Monitoring

### DeepSeek API
- Monitor usage at: https://platform.deepseek.com/usage
- Current key: `z5ajcjwbOd8DAjpat2YPh5PzKv84IvRk`
- Expected cost: ~$6/month for 100 articles/day

### Vercel
- Free tier includes: 100GB bandwidth, 100 hours serverless execution
- Monitor usage in Vercel dashboard → Usage tab

### Database
- Vercel Postgres: 60 compute hours/month free
- Neon: 0.5GB storage free
- Supabase: 500MB database free

## Next Steps

1. ✅ Customize the frontend styling if desired
2. ✅ Add more news sources by creating new scrapers
3. ✅ Set up custom domain in Vercel settings
4. ✅ Configure email alerts for scraping failures
5. ✅ Add analytics (Vercel Analytics is free)

## Support

If you encounter issues:
1. Check Vercel logs
2. Check GitHub Actions logs
3. Review this troubleshooting guide
4. Check the main README.md for more details

---

**Deployment Complete!** 🎉

Your Robotics Daily Report is now live and will automatically update daily with fresh robotics news!
