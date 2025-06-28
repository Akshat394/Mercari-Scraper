# Mercari Japan Shopping Assistant

A bilingual AI-powered shopping assistant for Mercari Japan built with Streamlit and OpenAI GPT-4o.

## Features

- **Bilingual Support**: Accept queries in English or Japanese
- **Smart Query Parsing**: Uses LLM to extract product filters and search parameters
- **Translation**: Automatically translates English queries to Japanese for effective Mercari searches
- **Product Ranking**: Intelligent ranking based on relevance, price, condition, and seller rating
- **AI Recommendations**: GPT-4o generates personalized product recommendations with explanations
- **Chat Interface**: Interactive chat-like interface with message history
- **Real-time Processing**: Progress indicators and responsive UI

## Setup

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone or download the project files

2. Set up your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. Run the application:
   ```bash
   streamlit run app.py --server.port 5000
   ```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Type your product query in English or Japanese in the chat input
2. The assistant will:
   - Parse your query to extract product criteria
   - Translate to Japanese if needed for Mercari search
   - Find matching products from the database
   - Rank products based on multiple factors
   - Generate personalized recommendations
3. View the top 3 product recommendations with detailed explanations

### Example Queries

**English:**
- "I'm looking for a gaming laptop under $1500"
- "Show me vintage Champion hoodies in good condition"
- "Find iPhone 14 Pro Max with high seller ratings"

**Japanese:**
- "1500ドル以下のゲーミングノートパソコンを探しています"
- "状態の良いヴィンテージのチャンピオンパーカーを見せて"
- "売り手評価の高いiPhone 14 Pro Maxを見つけて"

## Project Structure

