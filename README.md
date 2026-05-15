# Tabayun Backend - Legal Awareness Platform API ⚖️🤖

## Overview
**Tabayun (تباين)** is a high-performance legal awareness platform built with FastAPI. It aims to help tourists and residents understand and compare Saudi laws with international laws (e.g., Germany, UK) using cutting-edge AI and Semantic Search technologies.

## 🚀 Key Features
- **RAG Chatbot:** Intelligent legal assistant using Retrieval-Augmented Generation (Gemini AI + pgvector).
- **Semantic Search:** Multi-language search that understands legal intent, powered by `sentence-transformers`.
- **Legal Comparison:** Automated AI-driven comparison between Saudi and foreign legal articles.
- **Admin Dashboard:** Full management system for laws, users, audit logs, and AI prompt configurations.
- **Smart Scrapers:** Integrated Scrapy spiders for fetching legal data from official sources (SA, DE, UK).
- **Notifications:** In-app and Email notifications (via Resend).

## 🛠️ Tech Stack
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL with **pgvector** extension.
- **ORM:** SQLAlchemy.
- **AI/LLM:** Google Gemini (Flash 2.0/3.1).
- **Embeddings:** Multilingual Sentence Transformers (Local).
- **Validation:** Pydantic v2.

## ⚙️ Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL with `pgvector` extension installed.

### Installation
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Tabayun_BackEnd
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   GEMINI_API_KEY=your_gemini_key
   EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
   RESEND_API_KEY=your_resend_key
   ```

5. **Initialize Database:**
   ```bash
   python app/db/database.py
   ```

6. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📂 Project Structure
- `app/api/`: API route definitions (v1).
- `app/services/`: Business logic (AI, Vector Search, Admin services).
- `app/core/`: Security, RAG pipeline, and configuration.
- `app/db/`: Database models and connection setup.
- `scraper/`: Scrapy spiders and pipelines for data collection.
- `scripts/`: Maintenance and processing scripts (Vectorization, Simplification).

## 📄 License
This project is licensed under the MIT License.
