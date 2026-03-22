INSERT INTO documents (
    source_type, title, filename, filepath, year, month, week, speaker, seminar_date, title_embedding
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
RETURNING id;