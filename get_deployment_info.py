#!/usr/bin/env python3
"""
Helper script to get deployment information for Streamlit Cloud
"""

import os
from backend.config import DB_URL

def get_deployment_info():
    """Get deployment information for Streamlit Cloud"""
    print("🚀 Streamlit Cloud Deployment Information")
    print("=" * 50)
    
    # Get database URL from config
    try:
        print(f"📊 Database URL: {DB_URL}")
        print("\n✅ Your database is already configured!")
        print("\n📋 Environment Variables for Streamlit Cloud:")
        print("=" * 50)
        print(f"DATABASE_URL={DB_URL}")
        print("\nOptional (for chat features):")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        
    except Exception as e:
        print(f"❌ Error getting database info: {e}")
        print("\n📋 You'll need to set these environment variables:")
        print("=" * 50)
        print("DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require")
        print("OPENAI_API_KEY=your_openai_api_key_here (optional)")
    
    print("\n🎯 Next Steps:")
    print("1. Go to https://share.streamlit.io")
    print("2. Sign in with GitHub")
    print("3. Click 'New app'")
    print("4. Select your repository: Akshat394/Mercari-Scraper")
    print("5. Set the environment variables above")
    print("6. Deploy!")
    
    print("\n📝 Important Notes:")
    print("- Your database URL contains sensitive credentials")
    print("- Keep it secure and don't share it publicly")
    print("- The app will work without OpenAI API key (limited chat features)")

if __name__ == "__main__":
    get_deployment_info() 