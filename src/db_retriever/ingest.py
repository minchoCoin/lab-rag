import argparse
import re
from pathlib import Path

from tqdm import tqdm

from config import TEXT_ROOTS
from db import connect_db, ensure_schema, get_existing_filepaths, load_sql
from embed import load_embedder, embed_documents
from utils import iter_txt_files, parse_metadata, clean_text, chunk_text, split_by_speaker


DELETE_EXISTING_DOC_SQL = load_sql("delete_existing_doc.sql")
INSERT_DOCUMENT_SQL = load_sql("insert_document.sql")
INSERT_CHUNK_SQL = load_sql("insert_chunk.sql")


def build_rows_for_lab_seminar(document_id: int, meta: dict, text: str, model) -> list[tuple]:
    chunks = chunk_text(text)
    if not chunks:
        return []

    vectors = embed_documents(model, chunks)

    rows = []
    for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
        rows.append(
            (
                document_id,
                idx,
                chunk,
                chunk,  # content_tsv 생성용
                vector,
                meta["source_type"],
                meta["year"],
                meta["month"],
                meta["week"],
                meta["title"],
                meta["filename"],
                meta["filepath"],
                meta["speaker"],
                meta["seminar_date"],
            )
        )
    return rows


def build_rows_for_weekly_report(document_id: int, meta: dict, text: str, model) -> list[tuple]:
    speaker_blocks = split_by_speaker(text)

    rows = []
    chunk_index = 0

    for speaker, block_text in speaker_blocks:
        block_text = clean_text(block_text)
        if not block_text:
            continue

        chunks = chunk_text(block_text)
        if not chunks:
            continue

        vectors = embed_documents(model, chunks)

        for chunk, vector in zip(chunks, vectors):
            rows.append(
                (
                    document_id,
                    chunk_index,
                    chunk,
                    chunk,  # content_tsv 생성용
                    vector,
                    meta["source_type"],
                    meta["year"],
                    meta["month"],
                    meta["week"],
                    meta["title"],
                    meta["filename"],
                    meta["filepath"],
                    speaker,               # weekly_report는 chunk 단위 speaker
                    meta["seminar_date"],  # weekly_report는 보통 None
                )
            )
            chunk_index += 1

    return rows


def ingest_file(conn, model, path: Path, source_type: str):
    meta = parse_metadata(path, source_type)

    text = path.read_text(encoding="utf-8", errors="ignore")
    text = clean_text(text)
    if not text:
        print(f"[SKIP] 빈 파일: {path}")
        return
    title_vector = embed_documents(model, [meta["title"]])[0]
    with conn.cursor() as cur:
        # 기존 문서 삭제 후 재삽입
        cur.execute(DELETE_EXISTING_DOC_SQL, (meta["filepath"],))

        cur.execute(
            INSERT_DOCUMENT_SQL,
            (
                meta["source_type"],
                meta["title"],
                meta["filename"],
                meta["filepath"],
                meta["year"],
                meta["month"],
                meta["week"],
                meta["speaker"],        # lab_seminar만 값 있음
                meta["seminar_date"],   # lab_seminar만 값 있음
                title_vector,
            ),
        )
        document_id = cur.fetchone()[0]

        if source_type == "weekly_report":
            rows = build_rows_for_weekly_report(document_id, meta, text, model)
        else:
            rows = build_rows_for_lab_seminar(document_id, meta, text, model)

        if not rows:
            conn.rollback()
            print(f"[SKIP] 청크 없음: {path}")
            return

        cur.executemany(INSERT_CHUNK_SQL, rows)

    conn.commit()
    print(f"[OK] {path} -> doc_id={document_id}, chunks={len(rows)}")


def main():
    parser = argparse.ArgumentParser(description="Ingest text files into PostgreSQL + pgvector")
    parser.add_argument(
        "--refresh-all",
        action="store_true",
        help="기존 filepath가 있어도 전부 다시 적재",
    )
    args = parser.parse_args()

    print("[INFO] 임베딩 모델 로딩 중...")
    model = load_embedder()

    print("[INFO] DB 연결 중...")
    conn = connect_db()
    ensure_schema(conn)

    try:
        existing_filepaths = get_existing_filepaths(conn)

        for root, source_type in TEXT_ROOTS:
            files = list(iter_txt_files(root))

            if args.refresh_all:
                target_files = files
            else:
                target_files = [
                    path for path in files
                    if str(path).replace("\\", "/") not in existing_filepaths
                ]

            print(f"[INFO] {root} 전체 파일 수: {len(files)}")
            print(f"[INFO] {root} 적재 대상 파일 수: {len(target_files)}")

            for path in tqdm(target_files, desc=f"Ingest {source_type}"):
                ingest_file(conn, model, path, source_type)

    finally:
        conn.close()


if __name__ == "__main__":
    main()