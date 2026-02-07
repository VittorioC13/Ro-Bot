# How to Rename Your GitHub Repo (Optional)

If you want to rename from "Ro-Bot" to something without hyphens:

## Option 1: Rename on GitHub (Easiest)

1. Go to: https://github.com/VittorioC13/Ro-Bot/settings
2. Scroll to "Repository name"
3. Change to one of these:
   - `RoBot` (no space or hyphen)
   - `robotics_report` (underscore is fine)
   - `robotics-daily` (hyphens OK in repo, just not Vercel project names)
4. Click "Rename"

GitHub will automatically redirect the old URL!

## Option 2: Update Local Git Remote

After renaming on GitHub, update your local repository:

```bash
cd robotics-report
git remote set-url origin https://github.com/VittorioC13/[NEW-NAME].git
```

Replace `[NEW-NAME]` with whatever you renamed it to.

## Recommendation

**You don't need to rename!** Just use a different project name in Vercel:
- GitHub repo: `Ro-Bot` (can stay as is)
- Vercel project: `robotics-report` (no hyphen issues)

They don't have to match!
