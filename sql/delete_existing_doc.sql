DELETE FROM documents
WHERE filepath = %s
RETURNING id;