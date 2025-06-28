# Quick Deployment Guide

## For Cursor/Local Development

### 1. Install Dependencies
```bash
pip install streamlit openai psycopg2-binary sqlalchemy anthropic trafilatura
```

### 2. Environment Setup
Create `.env` file:
```
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```

### 3. Run Locally
```bash
streamlit run app.py --server.port 5000
```

## For Replit Deployment

1. **Set Environment Variables in Replit Secrets:**
   - `OPENAI_API_KEY`: Your OpenAI API key
   - Database variables are already configured

2. **Deploy:**
   - Click the "Deploy" button in Replit
   - Choose "Autoscale Deployment"
   - Your app will be live at `https://your-app-name.replit.app`

## Current Dependencies
- streamlit==1.40.2
- openai==1.57.4
- psycopg2-binary==2.9.10
- sqlalchemy==2.0.36
- anthropic==0.39.0
- trafilatura==1.12.2

## Testing Checklist
- [ ] App loads without errors
- [ ] Dark blue theme displays correctly
- [ ] Product showcase tabs work
- [ ] Chat functionality responds to queries
- [ ] Database contains 24 sample products
- [ ] All text is visible and readable

## Quick Commands
```bash
# Local development
streamlit run app.py --server.port 5000

# Check database connection
python -c "from core.database import DatabaseManager; db = DatabaseManager(); print(f'Products: {len(db.get_all_products())}')"
```