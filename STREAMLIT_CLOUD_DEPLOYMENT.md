# Streamlit Cloud Deployment Guide

## 🚀 Quick Deployment to Streamlit Cloud

### Step 1: Prepare Your Repository
Your code is already ready for deployment! The following files are properly configured:
- ✅ `app.py` - Main Streamlit application
- ✅ `requirements.txt` - Dependencies
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ All core modules are properly structured

### Step 2: Push to GitHub
If your code isn't already on GitHub:
```bash
git add .
git commit -m "Ready for Streamlit Cloud deployment"
git push origin main
```

### Step 3: Deploy on Streamlit Cloud

1. **Visit Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Connect Your Repository**
   - Click "New app"
   - Select your GitHub repository: `MercariScraper`
   - Set the main file path: `app.py`
   - Set the Python version: `3.12`

3. **Configure Environment Variables**
   Click "Advanced settings" and add:
   ```
   OPENAI_API_KEY = your_openai_api_key_here
   DATABASE_URL = your_postgresql_connection_string
   ```

4. **Deploy!**
   - Click "Deploy!"
   - Wait for the build to complete (usually 2-3 minutes)

### Step 4: Database Setup

Since Streamlit Cloud doesn't provide databases, you'll need an external PostgreSQL service:

#### Option A: Neon (Recommended - Free)
1. Go to [neon.tech](https://neon.tech)
2. Create a free account
3. Create a new project
4. Copy the connection string
5. Add it as `DATABASE_URL` in Streamlit Cloud

#### Option B: Supabase (Free Tier)
1. Go to [supabase.com](https://supabase.com)
2. Create a free account
3. Create a new project
4. Get the PostgreSQL connection string
5. Add it as `DATABASE_URL` in Streamlit Cloud

#### Option C: Railway (Free Tier)
1. Go to [railway.app](https://railway.app)
2. Create a PostgreSQL service
3. Get the connection string
4. Add it as `DATABASE_URL` in Streamlit Cloud

### Step 5: Test Your Deployment

Once deployed, your app will be available at:
```
https://your-app-name-your-username.streamlit.app
```

## 🔧 Environment Variables

### Required Variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: PostgreSQL connection string

### Optional Variables:
- `LLM_MOCK_MODE`: Set to "1" for testing without OpenAI API

## 🐛 Troubleshooting

### Common Issues:

1. **Build Fails**
   - Check that all dependencies are in `requirements.txt`
   - Ensure Python version is compatible (3.12 recommended)

2. **Database Connection Error**
   - Verify `DATABASE_URL` format
   - Check if database is accessible from external connections
   - Ensure SSL is enabled for cloud databases

3. **OpenAI API Error**
   - Verify your API key is valid
   - Check your OpenAI account has sufficient credits

4. **App Not Loading**
   - Check Streamlit Cloud logs
   - Verify `app.py` is the correct main file
   - Ensure no syntax errors in your code

### Debug Mode:
Add this to your app.py for debugging:
```python
import streamlit as st
st.set_option('deprecation.showPyplotGlobalUse', False)
```

## 📊 Monitoring

### Streamlit Cloud Features:
- **Automatic deployments** when you push to GitHub
- **Built-in logging** in the Streamlit Cloud dashboard
- **Performance monitoring** available in the dashboard
- **Custom domain** support (paid plans)

### Best Practices:
1. **Use environment variables** for all sensitive data
2. **Test locally** before deploying
3. **Monitor your app** regularly
4. **Keep dependencies updated**
5. **Use caching** for expensive operations

## 🔄 Continuous Deployment

Your app will automatically redeploy when you:
1. Push changes to your GitHub repository
2. Update the main branch
3. Modify `requirements.txt`

## 💰 Cost Considerations

### Streamlit Cloud Pricing:
- **Free Tier**: 
  - 3 apps per workspace
  - 1GB RAM per app
  - 200MB file size limit
  - Community support

- **Pro Plan** ($10/month):
  - Unlimited apps
  - 4GB RAM per app
  - 1GB file size limit
  - Priority support
  - Custom domains

## 🎉 Success!

Once deployed, your Mercari Japan Shopping Assistant will be:
- ✅ Accessible worldwide
- ✅ Automatically updated
- ✅ Professionally hosted
- ✅ Scalable and reliable

Your app URL will be shared in the Streamlit Cloud dashboard after successful deployment. 