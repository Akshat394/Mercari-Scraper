# 🚀 Streamlit Cloud Deployment Guide

## 📋 Prerequisites
- ✅ GitHub repository: `Akshat394/Mercari-Scraper`
- ✅ PostgreSQL database (already configured)
- ✅ All code committed and pushed to GitHub

## 🎯 Step-by-Step Deployment

### Step 1: Access Streamlit Cloud
1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Sign in with your **GitHub account**
3. Click **"New app"**

### Step 2: Configure Your App
1. **Repository**: Select `Akshat394/Mercari-Scraper`
2. **Branch**: `main`
3. **Main file path**: `app.py`
4. **App URL**: Choose a unique URL (e.g., `mercari-japan-ai`)

### Step 3: Set Environment Variables
Click **"Advanced settings"** and add these environment variables:

#### Required:
```
DATABASE_URL=postgresql://database_owner:npg_EQSL90iRFWVp@ep-spring-morning-a8c42kzl-pooler.eastus2.azure.neon.tech/database?sslmode=require&channel_binding=require
```

#### Optional (for enhanced chat features):
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 4: Deploy
1. Click **"Deploy!"**
2. Wait for the build process (2-3 minutes)
3. Your app will be available at: `https://your-app-name.streamlit.app`

## 🔧 Configuration Details

### App Settings
- **Python version**: 3.11.7 (specified in `runtime.txt`)
- **Dependencies**: Listed in `requirements.txt`
- **Playwright browsers**: Will be installed automatically

### Database Connection
- **Provider**: Neon (PostgreSQL)
- **Connection**: Pooled connection for better performance
- **SSL**: Required and configured

## 🧪 Post-Deployment Testing

### Test These Features:
1. **✅ App loads** without errors
2. **✅ Database connection** working
3. **✅ Product search** functional
4. **✅ Product display** working
5. **✅ Cart functionality** working
6. **✅ User feedback** system working

### Expected Behavior:
- App should load in 10-15 seconds
- Search should return results quickly
- Products should display with images and prices
- Cart should save items between sessions

## 🐛 Troubleshooting

### Common Issues:

#### 1. Build Fails
**Error**: "Module not found" or "Import error"
**Solution**: 
- Check `requirements.txt` has all dependencies
- Ensure all imports in `app.py` are correct
- Verify Python version in `runtime.txt`

#### 2. Database Connection Error
**Error**: "Connection refused" or "Authentication failed"
**Solution**:
- Verify `DATABASE_URL` is correct
- Check database is accessible from Streamlit Cloud
- Ensure SSL mode is set correctly

#### 3. Playwright Issues
**Error**: "Browser not found" or "Playwright install failed"
**Solution**:
- Playwright browsers are installed automatically
- If issues persist, check the logs for specific errors

#### 4. Memory Issues
**Error**: "Memory limit exceeded"
**Solution**:
- Reduce batch sizes in queries
- Implement pagination
- Optimize image loading

### Getting Help:
1. **Check logs** in Streamlit Cloud dashboard
2. **Verify environment variables** are set correctly
3. **Test locally** first: `streamlit run app.py`
4. **Check GitHub** for any recent issues

## 📊 Monitoring

### Streamlit Cloud Dashboard:
- **App status**: Running/Stopped
- **Build logs**: Recent deployment logs
- **Usage stats**: Viewer count, uptime
- **Error logs**: Any runtime errors

### Health Check:
Your app includes built-in health checks. Monitor these metrics:
- Page load times
- Search response times
- Database query performance
- Memory usage

## 🔄 Updates

### Automatic Updates:
- Streamlit Cloud automatically redeploys when you push to GitHub
- No manual intervention needed

### Manual Updates:
1. Make changes to your code
2. Commit and push to GitHub
3. Streamlit Cloud will automatically redeploy

## 🎉 Success!

Once deployed, your app will be available at:
```
https://your-app-name.streamlit.app
```

### Share Your App:
- **Public URL**: Share with anyone
- **GitHub**: Link to your repository
- **Documentation**: Include in your README

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Streamlit Cloud documentation
3. Check your app logs for specific errors
4. Verify all environment variables are set correctly

**Happy Deploying! 🚀**
