from sentence_transformers import SentenceTransformer

from config import EMBED_MODEL_NAME, BATCH_SIZE


def load_embedder() -> SentenceTransformer:
    return SentenceTransformer(EMBED_MODEL_NAME)


def embed_documents(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    embeddings = model.encode_document(
        texts,
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return [emb.tolist() for emb in embeddings]


def embed_query(model: SentenceTransformer, text: str) -> list[float]:
    emb = model.encode_query(
        [text],
        batch_size=1,
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0]
    return emb.tolist()