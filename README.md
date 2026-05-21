# AI Legal Q&A – Chat with Indian Laws

A full-stack AI application that allows users to ask legal questions about Indian laws and get grounded answers with citations.

## Features

- Semantic search using vector embeddings
- RAG (Retrieval-Augmented Generation) for accurate answers
- Chat-style interface
- Citations from relevant law sections
- Modern, responsive UI

## Tech Stack

- **Frontend**: React + Vite, Tailwind CSS
- **Backend**: Node.js + Express
- **Database**: Neon PostgreSQL with pgvector
- **AI**: Hugging Face for embeddings, OpenRouter for completions

## Setup

### Prerequisites

- Node.js
- Neon account
- Hugging Face API key (optional, for higher rate limits)
- OpenRouter API key

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
   Fill in your API keys and Neon connection string. Hugging Face API key is optional but recommended.

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   npm install
   ```

### Database Setup

1. Create a Neon project and copy its `DATABASE_URL`
2. Run the SQL setup script in the Neon SQL editor:
   ```sql
   -- Copy contents from scripts/setup.sql
   ```

3. Add the same `DATABASE_URL` to your root `.env` if you want to run the data scripts from the project root

4. Ingest legal data and generate embeddings:
   ```bash
   node scripts/insertAllLaws.js
   node scripts/generateEmbeddings.js
   ```

### Running the Application

1. Start the backend:
   ```bash
   cd backend
   npm run dev
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Open http://localhost:5173 in your browser

## API Endpoints

- `POST /api/ask` - Ask a legal question

## Deployment

- Backend can be deployed to services like Heroku, Vercel, or AWS
- Frontend can be deployed to Vercel or Netlify
- Database remains on Neon

## Disclaimer

This tool provides general legal information and is not legal advice. Always consult with a qualified legal professional for your specific situation.
