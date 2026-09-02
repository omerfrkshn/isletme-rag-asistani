CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    dataset TEXT NOT NULL,           -- 'kozsofra' | 'wikipedia'
    source_file TEXT NOT NULL,
    source_format TEXT NOT NULL,     -- 'text' | 'pdf' | 'image'
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(384) NOT NULL
);

CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS chunks_dataset_idx ON chunks (dataset);
