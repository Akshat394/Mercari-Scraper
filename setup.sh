#!/bin/bash

# Mercari Japan Shopping AI - Deployment Setup Script

echo "🚀 Setting up Mercari Japan Shopping AI..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p temp

# Set permissions
echo "🔐 Setting permissions..."
chmod +x setup.sh

echo "✅ Setup complete! Ready to deploy."

# Install Google Chrome
if ! command -v google-chrome > /dev/null; then
  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  sudo apt-get update
  sudo apt-get install -y ./google-chrome-stable_current_amd64.deb || true
fi

# Install ChromeDriver
if ! command -v chromedriver > /dev/null; then
  sudo apt-get update
  sudo apt-get install -y chromium-chromedriver || true
fi

mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"your-email@example.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml 