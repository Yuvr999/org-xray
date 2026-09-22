# =============================================================================
# ORG-XRAY — Render Deployment Guide
# =============================================================================

## Quick Deploy (Recommended)

### Prerequisites
1. A GitHub account with the repo pushed
2. A Render account (https://render.com — free tier available)
3. Your Gemini API key

### Step-by-Step

**1. Push to GitHub**
```bash
git remote add origin https://github.com/YOUR_USERNAME/org-xray.git
git add -A
git commit -m "Deploy: Add Render configuration"
git branch -M main
git push -u origin main
```

**2. Deploy on Render**
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repo (`org-xray`)
4. Render auto-detects `render.yaml` and creates:
   - 🗄️ **org-xray-db** — PostgreSQL database (free tier)
   - ⚡ **org-xray-api** — FastAPI backend
   - 🌐 **org-xray-web** — React frontend (static site)
5. Set the **GEMINI_API_KEY** manually in the API service's Environment tab

**3. After Deploy**
- Frontend: `https://org-xray-web.onrender.com`
- Backend API: `https://org-xray-api.onrender.com/api/v1/docs`
- The database is auto-connected via `DATABASE_URL`

### Environment Variables Reference

| Variable | Service | Set By | Description |
|----------|---------|--------|-------------|
| `DATABASE_URL` | API | Render (auto) | PostgreSQL connection string |
| `SECRET_KEY` | API | Render (auto) | JWT signing key |
| `GEMINI_API_KEY` | API | You (manual) | Google Gemini API key |
| `GEMINI_MODEL` | API | render.yaml | `gemini-2.5-flash` |
| `CORS_ORIGINS` | API | render.yaml | Allowed frontend origins |
| `VITE_API_URL` | Web | render.yaml | Backend URL for API calls |
| `ENVIRONMENT` | API | render.yaml | `production` |

### Notes
- **Free tier**: Services sleep after 15 min of inactivity. First request takes ~30s to wake.
- **Database**: Free tier has 256 MB storage, auto-deleted after 90 days of inactivity.
- **Upgrade**: Switch to Starter ($7/mo) for always-on services.
