#!/usr/bin/env bash

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

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