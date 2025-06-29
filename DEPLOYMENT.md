# 🚀 Mercari Japan Shopping AI - Deployment Guide

## 📋 Overview
This guide will help you deploy the Mercari Japan Shopping AI system to various platforms.

## 🎯 Quick Deploy Options

### Option 1: Streamlit Cloud (Recommended)
1. **Fork/Clone** this repository to your GitHub account
2. **Set up environment variables** in Streamlit Cloud:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `OPENAI_API_KEY`: Your OpenAI API key (optional, for chat features)
3. **Deploy** by connecting your GitHub repo to Streamlit Cloud

### Option 2: Heroku
1. **Install Heroku CLI**
2. **Create Heroku app**: `heroku create your-app-name`
3. **Set environment variables**:
   ```bash
   heroku config:set DATABASE_URL="your-postgresql-url"
   heroku config:set OPENAI_API_KEY="your-openai-key"
   ```
4. **Deploy**: `git push heroku main`

### Option 3: Railway
1. **Connect** your GitHub repository to Railway
2. **Set environment variables** in Railway dashboard
3. **Deploy** automatically on push

## 🔧 Environment Variables

### Required
- `DATABASE_URL`: PostgreSQL connection string
  ```
  postgresql://username:password@host:port/database?sslmode=require
  ```

### Optional
- `OPENAI_API_KEY`: For advanced chat features
- `STREAMLIT_SERVER_PORT`: Port number (default: 8501)

## 📦 Dependencies

The project uses these main dependencies:
- `streamlit`: Web interface
- `playwright`: Web scraping
- `sqlalchemy`: Database ORM
- `psycopg2-binary`: PostgreSQL adapter
- `openai`: AI chat features

## 🗄️ Database Setup

### PostgreSQL (Recommended)
1. **Create database** on your preferred provider (Neon, Supabase, etc.)
2. **Run migrations**:
   ```bash
   cd backend
   python -c "from models import Base; from config import engine; Base.metadata.create_all(engine)"
   ```
3. **Add SEO tags column**:
   ```bash
   python add_seo_tags_column.py
   ```

### Alternative: SQLite (Development)
For local development, you can use SQLite by modifying `backend/config.py`.

## 🔄 Data Population

### Option 1: Use Existing Scraped Data
The system comes with 325 pre-scraped products. No additional setup needed.

### Option 2: Scrape Fresh Data
```bash
cd backend
python scraper.py
python seo_tagger.py
```

## 🧪 Testing

Run the integration test before deployment:
```bash
python integration_test.py
```

## 📊 Monitoring

### Health Check
The app includes a health check endpoint at `/health`

### Logs
- **Streamlit Cloud**: View logs in the dashboard
- **Heroku**: `heroku logs --tail`
- **Railway**: View logs in the dashboard

## 🔒 Security Considerations

1. **Database credentials**: Never commit to git
2. **API keys**: Use environment variables
3. **Rate limiting**: Implement if needed for production
4. **CORS**: Configure appropriately for your domain

## 🚀 Performance Optimization

1. **Database indexing**: Ensure proper indexes on search columns
2. **Caching**: Use Streamlit's caching for expensive operations
3. **Connection pooling**: Already configured in the database manager
4. **Image optimization**: Consider CDN for product images

## 🐛 Troubleshooting

### Common Issues

1. **Database connection failed**
   - Check `DATABASE_URL` environment variable
   - Verify database is accessible from deployment platform

2. **Playwright not working**
   - Ensure `playwright install chromium` runs during deployment
   - Check if platform supports browser automation

3. **Memory issues**
   - Reduce batch sizes in scraper
   - Implement pagination for large datasets

### Support
- Check the logs for detailed error messages
- Verify all environment variables are set correctly
- Ensure all dependencies are installed

## 📈 Scaling

### Horizontal Scaling
- Use multiple Streamlit instances behind a load balancer
- Implement Redis for session management

### Database Scaling
- Use read replicas for query-heavy operations
- Implement database sharding if needed

## 🔄 Updates

### Automatic Updates
- Enable automatic deployments from GitHub
- Use semantic versioning for releases

### Manual Updates
1. **Pull latest changes**: `git pull origin main`
2. **Update dependencies**: `pip install -r requirements.txt`
3. **Run migrations**: Update database schema if needed
4. **Restart application**

## 📞 Support

For deployment issues:
1. Check the logs first
2. Verify environment variables
3. Test locally before deploying
4. Review the troubleshooting section above

---

**Happy Deploying! 🎉**