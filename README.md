# Mercari Japan Shopping Assistant

A bilingual AI-powered shopping assistant that helps users find products on Mercari Japan with natural language queries in English or Japanese.

## Features

- 🤖 AI-powered product search and recommendations using OpenAI GPT-4o
- 🌐 Bilingual support (English/Japanese) with automatic language detection
- 🛍️ Product showcase with categorized browsing
- 💾 PostgreSQL database with 24+ sample products
- 🎨 Beautiful dark blue theme with excellent contrast
- 📱 Responsive chat interface built with Streamlit

## Prerequisites

- Python 3.11+
- PostgreSQL database
- OpenAI API key

## Local Development Setup (Cursor)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd mercari-shopping-assistant

# Install Python dependencies
pip install -r requirements.txt
# or if using uv:
uv sync
```

### 2. Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# PostgreSQL Database (required)
DATABASE_URL=postgresql://username:password@localhost:5432/mercari_db
PGHOST=localhost
PGPORT=5432
PGUSER=your_username
PGPASSWORD=your_password
PGDATABASE=mercari_db
```

### 3. Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE mercari_db;
```

The app will automatically create tables and populate sample data on first run.

### 4. Run the Application

```bash
# Start the Streamlit app
streamlit run app.py --server.port 5000

# Or use the specific configuration
streamlit run app.py --server.port 5000 --server.address 0.0.0.0
```

Visit `http://localhost:5000` in your browser.

### 5. Development Tips

- The app uses caching for services - restart if you modify core modules
- Check `.streamlit/config.toml` for theme and server configuration
- Database schema is defined in `core/database.py`
- Sample data is in `core/sample_data.py`

## Project Structure

```
├── app.py                  # Main Streamlit application
├── core/
│   ├── database.py         # Database models and operations
│   ├── data_handler.py     # Data retrieval and processing
│   ├── llm_service.py      # OpenAI integration
│   ├── product_ranker.py   # Product ranking algorithm
│   ├── sample_data.py      # Sample product data
│   └── translator.py       # Translation services
├── utils/
│   └── helpers.py          # Utility functions
├── .streamlit/
│   └── config.toml         # Streamlit configuration
└── requirements.txt        # Python dependencies
```

## Deployment Instructions

### Option 1: Replit Deployment (Recommended)

1. **Prepare for Deployment:**
   - Ensure all environment variables are set in Replit Secrets
   - Verify the app runs without errors locally

2. **Deploy on Replit:**
   - Click the "Deploy" button in your Replit workspace
   - Choose "Autoscale Deployment" for production use
   - The app will be available at `https://your-app-name.replit.app`

### Option 2: Heroku Deployment

1. **Setup Heroku:**
   ```bash
   # Install Heroku CLI
   npm install -g heroku
   
   # Login to Heroku
   heroku login
   
   # Create a new app
   heroku create your-app-name
   ```

2. **Add PostgreSQL:**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

3. **Set Environment Variables:**
   ```bash
   heroku config:set OPENAI_API_KEY=your_openai_api_key
   ```

4. **Create Procfile:**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

5. **Deploy:**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### Option 3: Railway Deployment

1. **Connect to Railway:**
   - Visit [railway.app](https://railway.app)
   - Connect your GitHub repository
   - Add PostgreSQL service

2. **Environment Variables:**
   - Set `OPENAI_API_KEY` in Railway dashboard
   - Railway will automatically set PostgreSQL variables

3. **Deploy:**
   - Railway automatically deploys on git push

### Option 4: Docker Deployment

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 5000
   CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]
   ```

2. **Build and Run:**
   ```bash
   docker build -t mercari-assistant .
   docker run -p 5000:5000 --env-file .env mercari-assistant
   ```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4o |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `PGHOST` | Yes | PostgreSQL host |
| `PGPORT` | Yes | PostgreSQL port (usually 5432) |
| `PGUSER` | Yes | PostgreSQL username |
| `PGPASSWORD` | Yes | PostgreSQL password |
| `PGDATABASE` | Yes | PostgreSQL database name |

## API Keys Setup

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to your environment variables

### Database Access
- For local development: Install PostgreSQL locally
- For production: Use hosted PostgreSQL (Heroku Postgres, Railway, etc.)

## Testing

Test the application by:
1. Asking product questions in English: "I want to buy a Nintendo Switch"
2. Asking in Japanese: "新しいiPhoneが欲しいです"
3. Browsing the product showcase tabs
4. Checking that all text is visible in the dark theme

## Troubleshooting

- **API Errors:** Verify your OpenAI API key is valid and has credits
- **Database Issues:** Check PostgreSQL connection and credentials
- **Import Errors:** Ensure all dependencies are installed
- **Port Issues:** Use port 5000 for Replit deployment compatibility

## Support

For issues or questions, check the logs in your deployment platform or run locally to debug.