# Leads Personified

A webapp for lead enrichment and ranking.

## Features
- Upload/download Excel files
- Lead enrichment and ranking (OpenAI API)
- Local SQLite database
- All processing in backend

## Setup

### Backend
- Python 3.8+
- FastAPI, SQLAlchemy, SQLite, OpenAI, pandas, openpyxl
- Install dependencies from `backend/requirements.txt`
- Environment variables in `.env`

### Frontend
- React (see `frontend/`)

## Environment Variables
All sensitive keys and configuration are stored in `.env`.

- `TAVILY_API_KEY`: API key for TavilySearch. Used to search for company websites when not provided in the lead data. Obtain your API key from https://app.tavily.com/ and add it to your `.env` file.
- `OPENAI_API_KEY`: API key for OpenAI. Used to generate buyer personas from company webpage text using GPT-4o-mini. Obtain your API key from https://platform.openai.com/ and add it to your `.env` file.

## Backend Dependencies

- `requests`: For making HTTP requests (TavilySearch API, web scraping)
- `beautifulsoup4`: For extracting text from HTML web pages
- `openai`: For generating buyer personas using GPT-4o-mini

## Database Schema
- See `database_schema_mods.md` and `database_schema_mods.sql` for schema and changes.

## Usage
- Start backend: `uvicorn backend.main:app --reload`
- Start frontend: `cd frontend && npm start` 