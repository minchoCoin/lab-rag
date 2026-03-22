CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    source_type TEXT NOT NULL,
    title TEXT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL UNIQUE,
    year INT,
    month INT,
    week INT,
    speaker TEXT,
    seminar_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    title_embedding vector(1024)
);

CREATE TABLE IF NOT EXISTS chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    content_tsv tsvector,
    embedding vector(1024),
    source_type TEXT NOT NULL,
    year INT,
    month INT,
    week INT,
    title TEXT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    speaker TEXT,
    seminar_date DATE
);

CREATE INDEX IF NOT EXISTS idx_documents_source_type
ON documents(source_type);

CREATE INDEX IF NOT EXISTS idx_documents_year_month_week
ON documents(year, month, week);

CREATE INDEX IF NOT EXISTS idx_documents_title_embedding_hnsw
ON documents USING hnsw (title_embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_chunks_source_type
ON chunks(source_type);

CREATE INDEX IF NOT EXISTS idx_chunks_year_month_week
ON chunks(year, month, week);

CREATE INDEX IF NOT EXISTS idx_chunks_content_tsv
ON chunks USING GIN (content_tsv);

CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
ON chunks USING hnsw (embedding vector_cosine_ops);