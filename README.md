# Tabayun Backend - Legal Awareness Platform API

## Overview
Tabayun Backend is a high-performance RESTful API built with FastAPI that powers a multilingual legal awareness platform for foreign tourists.

## Tech Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL + pgvector
- **ORM:** SQLAlchemy
- **AI/LLM:** Claude 3.5 Sonnet (via LangChain)
- **Embeddings:** OpenAI text-embedding-3-small
- **Migrations:** Alembic

## Getting Started
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in the values
6. Run the application: `uvicorn app.main:app --reload`
