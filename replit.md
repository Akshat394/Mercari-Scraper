# Mercari Japan Shopping Assistant

## Overview

A bilingual AI-powered shopping assistant application that helps users find products on Mercari Japan. Built with Streamlit for the frontend and Python for backend logic, integrating OpenAI GPT-4o for natural language understanding, query parsing, and product recommendations.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for web UI
- **Interface Pattern**: Chat-based interaction using `st.chat_message()` and `st.chat_input()`
- **State Management**: Streamlit session state for chat history persistence
- **Layout**: Wide layout with responsive design

### Backend Architecture
- **Modular Design**: Core business logic separated into distinct service modules
- **Service Layer**: Dedicated services for LLM operations, data handling, product ranking, and translation
- **Language Detection**: Simple character-based algorithm for English/Japanese detection
- **Caching**: Streamlit resource caching for service initialization

### Data Storage Solutions
- **Database**: PostgreSQL database with SQLAlchemy ORM
- **Schema**: Products table with fields for id, name, price, condition, seller_rating, category, brand, image_url, url, description
- **Data Management**: DatabaseManager class handles all database operations
- **Initialization**: Automatically populated with sample product data on first run

## Key Components

### Core Services

1. **LLMService** (`core/llm_service.py`)
   - OpenAI GPT-4o integration for query parsing and recommendations
   - JSON-structured responses for consistent data handling
   - Function calling capabilities for structured output

2. **DataHandler** (`core/data_handler.py`)
   - Database integration layer for product operations
   - Product search and retrieval from PostgreSQL
   - Interface between application logic and database

3. **ProductRanker** (`core/product_ranker.py`)
   - Multi-criteria scoring system
   - Weighted ranking based on relevance, price, condition, and seller rating
   - Duplicate removal functionality

4. **Translator** (`core/translator.py`)
   - Bilingual query translation using LLM
   - Japanese search optimization for Mercari platform
   - Fallback mechanisms for translation failures

### Utilities
- **Language Detection**: Character-based algorithm for Japanese/English identification
- **Data Formatting**: Price formatting, product display helpers
- **Query Processing**: Text cleaning and price range extraction

## Data Flow

1. **User Input**: User submits query in English or Japanese via chat interface
2. **Language Detection**: System identifies input language using character analysis
3. **Query Parsing**: LLM extracts structured filters and search parameters from natural language
4. **Translation**: English queries translated to Japanese for effective Mercari searching
5. **Product Search**: Data handler queries PostgreSQL database for matching products
6. **Ranking**: Products scored and ranked using weighted multi-criteria algorithm
7. **AI Recommendation**: Top products sent to LLM for personalized recommendation generation
8. **Display**: Results presented in chat interface with formatted product information

## External Dependencies

### AI Services
- **OpenAI API**: GPT-4o model for natural language processing
- **Authentication**: Environment variable-based API key management

### Python Libraries
- **Streamlit**: Web application framework
- **OpenAI**: Official OpenAI Python client
- **SQLAlchemy**: ORM for database operations
- **psycopg2-binary**: PostgreSQL database adapter
- **Standard Libraries**: json, os, re, typing, math

### Database
- **PostgreSQL**: Primary data storage for product information
- **Environment Variables**: DATABASE_URL, PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE

## Deployment Strategy

### Development Setup
- Local development using Streamlit dev server
- Environment variable configuration for API keys
- Port configuration (default: 5000)

### Production Considerations
- API key security and rotation
- Rate limiting for OpenAI API calls
- Caching strategies for improved performance
- Error handling and graceful degradation

### Scalability
- Modular architecture supports easy component replacement
- Service-based design allows for microservices migration
- Caching layer ready for production optimization

## Changelog
- June 28, 2025: Initial setup with Streamlit UI and OpenAI integration
- June 28, 2025: Added PostgreSQL database with SQLAlchemy ORM for persistent product storage
- June 28, 2025: Enhanced UI with product showcase section, improved styling, and fixed contrast issues
- June 28, 2025: Finalized design with proper accessibility and visual hierarchy

## User Preferences

Preferred communication style: Simple, everyday language.