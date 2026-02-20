# Deployment Guide

## Live Demo Dashboard

### Option 1: Streamlit Cloud (Recommended)

1. **Fork the repository** on GitHub

2. **Go to** [share.streamlit.io](https://share.streamlit.io)

3. **Deploy**:
   - Click "New app"
   - Select your forked repo
   - Main file path: `civicspend/ui/app.py`
   - Click "Deploy"

4. **Done!** Your dashboard will be live at `https://[your-app-name].streamlit.app`

### Option 2: Local Demo

```bash
# Install dependencies
pip install -r requirements.txt
pip install -e .

# Run dashboard
streamlit run civicspend/ui/app.py
```

Dashboard opens at `http://localhost:8501`

### Option 3: Docker (Production)

```bash
# Build image
docker build -t civicspend .

# Run container
docker run -p 8501:8501 civicspend
```

## Demo Data

The dashboard automatically generates demo data on first run:
- 12 Minnesota vendors
- 24 months of spending data
- 3 injected anomalies

## Configuration

Edit `.streamlit/config.toml` to customize:
- Theme colors
- Port
- CORS settings

## Troubleshooting

### "No data available"
Run: `civicspend ingest --mock`

### Import errors
Run: `pip install -e .`

### Port already in use
Change port in `.streamlit/config.toml`

## Public Access

To share your dashboard:

1. **Streamlit Cloud**: Automatic public URL
2. **Heroku**: See `docs/HEROKU_DEPLOY.md`
3. **AWS/GCP**: See `docs/CLOUD_DEPLOY.md`

## Security Notes

- Demo data is synthetic (no real PII)
- All data is public domain (USAspending.gov)
- No authentication required for demo
- Add auth for production deployment
