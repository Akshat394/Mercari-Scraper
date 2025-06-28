# Deployment Guide for Mercari Japan Shopping Assistant

## Quick Deployment Options

### 1. Streamlit Cloud (Recommended)
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set environment variables:
   - `OPENAI_API_KEY`
   - `DATABASE_URL`
5. Deploy!

### 2. Railway
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Add PostgreSQL service
4. Set environment variables
5. Deploy automatically

### 3. Render
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repository
4. Use `render.yaml` configuration
5. Set environment variables
6. Deploy!

## Environment Variables Required

```bash
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=your_postgresql_connection_string
```

## Database Setup

### For Production Database:
- **Railway**: Built-in PostgreSQL service
- **Render**: PostgreSQL add-on
- **Heroku**: PostgreSQL add-on
- **Streamlit Cloud**: Use external PostgreSQL service

### Database Migration:
```bash
# Run database initialization
python -c "from core.database import init_db; init_db()"
```

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Enable HTTPS** in production
4. **Set up proper CORS** if needed
5. **Monitor application logs**

## Performance Optimization

1. **Database connection pooling**
2. **Caching frequently accessed data**
3. **Optimize image loading**
4. **Use CDN for static assets**

## Monitoring and Maintenance

1. **Set up logging** for error tracking
2. **Monitor database performance**
3. **Regular security updates**
4. **Backup database regularly**

## Troubleshooting

### Common Issues:
1. **Port binding errors**: Ensure `$PORT` environment variable is set
2. **Database connection**: Verify `DATABASE_URL` format
3. **API key issues**: Check OpenAI API key validity
4. **Memory limits**: Optimize for platform constraints

### Platform-Specific Notes:

#### Streamlit Cloud
- Maximum file size: 200MB
- Memory limit: 1GB
- No persistent file storage

#### Railway
- Good for full-stack applications
- PostgreSQL included
- Automatic deployments

#### Render
- Production-ready
- Good uptime guarantees
- PostgreSQL support

#### Heroku
- Mature platform
- Good documentation
- Paid service