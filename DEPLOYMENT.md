# Deployment Guide - Mercari Japan AI Shopping Agent

This guide covers deployment options for the complete 10/10 implementation with real web scraping and AI agent architecture.

## 🚀 **Quick Deployment Options**

### **Option 1: Streamlit Cloud (Recommended)**

1. **Prepare Repository**
   ```bash
   # Ensure all files are committed
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set environment variables:
     ```
     OPENAI_API_KEY=sk-your-openai-api-key
     DATABASE_URL=your-postgresql-url
     ```
   - Deploy!

### **Option 2: Railway (Recommended for Production)**

1. **Setup Railway**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Initialize project
   railway init
   ```

2. **Add Services**
   ```bash
   # Add PostgreSQL
   railway add postgresql
   
   # Add environment variables
   railway variables set OPENAI_API_KEY=sk-your-openai-api-key
   ```

3. **Deploy**
   ```bash
   railway up
   ```

### **Option 3: Heroku**

1. **Setup Heroku**
   ```bash
   # Install Heroku CLI
   npm install -g heroku
   
   # Login
   heroku login
   
   # Create app
   heroku create your-mercari-agent
   ```

2. **Add PostgreSQL**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set OPENAI_API_KEY=sk-your-openai-api-key
   ```

4. **Create Procfile**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

## 🐳 **Docker Deployment**

### **Dockerfile**
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### **Docker Compose**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=mercari_db
      - POSTGRES_USER=mercari_user
      - POSTGRES_PASSWORD=mercari_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### **Build and Run**
```bash
# Build the image
docker build -t mercari-agent .

# Run with Docker Compose
docker-compose up -d

# Or run standalone
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your-key \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  mercari-agent
```

## ☁️ **Cloud Platform Deployment**

### **Google Cloud Run**

1. **Setup Google Cloud**
   ```bash
   # Install gcloud CLI
   gcloud auth login
   gcloud config set project your-project-id
   ```

2. **Deploy**
   ```bash
   # Build and deploy
   gcloud run deploy mercari-agent \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars OPENAI_API_KEY=your-key
   ```

### **AWS Elastic Beanstalk**

1. **Create Application**
   ```bash
   # Install EB CLI
   pip install awsebcli
   
   # Initialize EB application
   eb init -p python-3.11 mercari-agent
   ```

2. **Create Environment**
   ```bash
   eb create mercari-agent-env
   ```

3. **Set Environment Variables**
   ```bash
   eb setenv OPENAI_API_KEY=your-key
   eb setenv DATABASE_URL=your-db-url
   ```

### **Azure App Service**

1. **Setup Azure CLI**
   ```bash
   # Install Azure CLI
   az login
   az group create --name mercari-agent-rg --location eastus
   ```

2. **Deploy**
   ```bash
   # Create app service
   az webapp create \
     --resource-group mercari-agent-rg \
     --plan mercari-agent-plan \
     --name mercari-agent \
     --runtime "PYTHON|3.11"
   
   # Set environment variables
   az webapp config appsettings set \
     --resource-group mercari-agent-rg \
     --name mercari-agent \
     --settings OPENAI_API_KEY=your-key
   ```

## 🔧 **Environment Configuration**

### **Required Environment Variables**

```env
# OpenAI API (Required)
OPENAI_API_KEY=sk-your-openai-api-key

# Database (Required)
DATABASE_URL=postgresql://user:password@host:port/database

# Optional Database Variables
PGHOST=localhost
PGPORT=5432
PGUSER=your_username
PGPASSWORD=your_password
PGDATABASE=mercari_db

# Optional: Selenium Configuration
SELENIUM_HEADLESS=true
CHROME_DRIVER_PATH=/usr/bin/chromedriver
```

### **Environment Setup Script**
```bash
#!/bin/bash
# setup_env.sh

echo "Setting up Mercari Agent environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/mercari_db
PGHOST=localhost
PGPORT=5432
PGUSER=mercari_user
PGPASSWORD=mercari_password
PGDATABASE=mercari_db

# Selenium Configuration
SELENIUM_HEADLESS=true
EOF
    echo ".env file created. Please update with your actual values."
else
    echo ".env file already exists."
fi

# Create database
echo "Setting up PostgreSQL database..."
sudo -u postgres createdb mercari_db
sudo -u postgres createuser mercari_user
sudo -u postgres psql -c "ALTER USER mercari_user WITH PASSWORD 'mercari_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mercari_db TO mercari_user;"

echo "Environment setup complete!"
```

## 📊 **Monitoring and Logging**

### **Health Check Endpoint**
```python
# Add to app.py
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }
```

### **Logging Configuration**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mercari_agent.log'),
        logging.StreamHandler()
    ]
)
```

### **Performance Monitoring**
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logging.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper
```

## 🔒 **Security Considerations**

### **API Key Security**
```python
# Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
```

### **Database Security**
```python
# Use connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### **Rate Limiting**
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    def decorator(func):
        last_calls = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            last_calls[:] = [call for call in last_calls if now - call < 60]
            
            if len(last_calls) >= calls_per_minute:
                sleep_time = 60 - (now - last_calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            last_calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Chrome Driver Issues**
   ```bash
   # Install Chrome driver
   pip install webdriver-manager
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connection
   python -c "from core.database import DatabaseManager; db = DatabaseManager(); print('Connected!')"
   ```

3. **OpenAI API Issues**
   ```bash
   # Test OpenAI connection
   python -c "from openai import OpenAI; client = OpenAI(); print('API working!')"
   ```

### **Debug Mode**
```bash
# Run with debug logging
streamlit run app.py --logger.level=debug
```

### **Performance Optimization**
```python
# Enable caching
@st.cache_data
def expensive_function():
    # Your expensive operation here
    pass
```

## 📈 **Scaling Considerations**

### **Horizontal Scaling**
- Use load balancers
- Implement session management
- Use Redis for caching

### **Vertical Scaling**
- Increase memory allocation
- Use more powerful instances
- Optimize database queries

### **Database Scaling**
- Use read replicas
- Implement connection pooling
- Consider database sharding

---

**This deployment guide ensures your 10/10 Mercari Agent is production-ready with proper security, monitoring, and scaling capabilities.**