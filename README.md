# AI Legal Q&A

AI Legal Q&A is a retrieval-augmented assistant for Indian law. The project now has a **Streamlit UI** at the repository root, while the existing Python legal search and answer-generation services remain in `python_backend/`.

## What This Project Contains

- `app.py` - the new Streamlit interface
- `python_backend/` - FastAPI-style backend modules reused directly by Streamlit
- `frontend/` - the older React/Vite client, kept as a legacy frontend
- `scripts/` - database setup and law-ingestion scripts

## Current User Flow

- Ask a legal question in the Streamlit chat UI
- Retrieve relevant law sections from Neon PostgreSQL with pgvector
- Generate an answer with citations using OpenRouter
- Browse laws in a searchable Laws Explorer view

## Tech Stack

- **UI**: Streamlit
- **Backend services**: Python
- **Database**: Neon PostgreSQL with pgvector
- **AI**: Hugging Face embeddings + OpenRouter completions

## Setup

### Prerequisites

- Python 3.10+
- Neon PostgreSQL database
- OpenRouter API key
- Hugging Face API key (optional, for higher embedding rate limits)

### Install Python Dependencies

```bash
cd python_backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
```

### Environment Variables

Copy `.env.example` to `.env` and set:

- `OPENROUTER_API_KEY`
- `HUGGINGFACE_API_KEY`
- `DATABASE_URL`
- `APP_URL`

`APP_URL` should usually stay at `http://localhost:8501` for the Streamlit app.

## Database Setup

1. Create a Neon project and copy its `DATABASE_URL`
2. Run the SQL in `scripts/setup.sql`
3. Ingest law data and generate embeddings:

```bash
node scripts/insertAllLaws.js
node scripts/generateEmbeddings.js
```

## Run The App

From the repository root:

```bash
streamlit run app.py
```

Then open `http://localhost:8501`.

## Optional Features

- Laws Explorer works with fallback bundled laws if the database is unavailable.
- Image OCR in Streamlit is designed as an optional enhancement path and requires both `pytesseract` and a local `tesseract` install.
- The React frontend in `frontend/` can still be used separately if needed.

## Legacy Backend API

If you still want to run the FastAPI backend directly:

```bash
cd python_backend
uvicorn main:app --reload --port 5000
```

Main endpoint:

- `POST /api/ask`

## Disclaimer

This tool provides general legal information and is not legal advice. Always consult a qualified legal professional for your specific situation.
