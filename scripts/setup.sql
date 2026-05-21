-- Create the laws table
CREATE TABLE IF NOT EXISTS laws (
  id BIGSERIAL PRIMARY KEY,
  act TEXT NOT NULL,
  section TEXT NOT NULL,
  title TEXT,
  content TEXT NOT NULL,
  keywords TEXT[],
  embedding VECTOR(384),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE laws ENABLE ROW LEVEL SECURITY;

-- Create the RPC function for vector search
CREATE OR REPLACE FUNCTION match_laws(query_embedding VECTOR(384), match_count INT DEFAULT 3)
RETURNS TABLE(content TEXT, act TEXT, section TEXT, similarity FLOAT)
LANGUAGE sql
AS $func$
  SELECT
    l.content,
    l.act,
    l.section,
    1 - (l.embedding <=> query_embedding) AS similarity
  FROM laws l
  WHERE l.embedding IS NOT NULL
  ORDER BY l.embedding <=> query_embedding
  LIMIT match_count;
$func$;

-- Create index for faster vector search
CREATE INDEX IF NOT EXISTS laws_embedding_idx ON laws USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);