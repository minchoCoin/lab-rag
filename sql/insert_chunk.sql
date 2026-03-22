INSERT INTO chunks (
    document_id, chunk_index, content, content_tsv, embedding,
    source_type, year, month, week, title, filename, filepath, speaker, seminar_date
)
VALUES (
    %s, %s, %s, to_tsvector('simple', %s), %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s
);