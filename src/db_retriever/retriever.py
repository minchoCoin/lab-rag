from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from db import connect_db
from embed import load_embedder, embed_query


@dataclass
class RetrievalFilters:
    source_type: str | None = None          # lab_seminar / weekly_report
    speaker: str | None = None
    seminar_date: str | None = None         # YYYY-MM-DD
    start_date: str | None = None           # YYYY-MM-DD
    end_date: str | None = None             # YYYY-MM-DD
    year: int | None = None
    month: int | None = None
    week: int | None = None
    filepath_keywords: list[str] | None = None


class Retriever:
    def __init__(self):
        self.model = load_embedder()

    # -----------------------------
    # 날짜 유틸
    # -----------------------------
    @staticmethod
    def get_this_week_range() -> tuple[str, str]:
        today = datetime.today().date()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start.isoformat(), end.isoformat()

    @staticmethod
    def get_month_range(year: int, month: int) -> tuple[str, str]:
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)
        return start.isoformat(), end.isoformat()

    # -----------------------------
    # 내부 WHERE 절 생성
    # -----------------------------
    def _build_where_clause(self, filters: RetrievalFilters) -> tuple[str, list[Any]]:
        clauses = ["1=1"]
        params: list[Any] = []

        if filters.source_type is not None:
            clauses.append("source_type = %s")
            params.append(filters.source_type)

        if filters.speaker is not None:
            clauses.append("speaker = %s")
            params.append(filters.speaker)

        if filters.seminar_date is not None:
            clauses.append("seminar_date = %s")
            params.append(filters.seminar_date)

        if filters.start_date is not None:
            clauses.append("seminar_date >= %s")
            params.append(filters.start_date)

        if filters.end_date is not None:
            clauses.append("seminar_date <= %s")
            params.append(filters.end_date)

        if filters.year is not None:
            clauses.append("year = %s")
            params.append(filters.year)

        if filters.month is not None:
            clauses.append("month = %s")
            params.append(filters.month)

        if filters.week is not None:
            clauses.append("week = %s")
            params.append(filters.week)
        if filters.filepath_keywords:
            keyword_clauses = []
            for kw in filters.filepath_keywords:
                keyword_clauses.append("filepath ILIKE %s")
                params.append(f"%{kw}%")
            clauses.append("(" + " OR ".join(keyword_clauses) + ")")
        return " AND ".join(clauses), params

    # -----------------------------
    # 메타데이터만 조회
    # -----------------------------
    def filter_only(self, filters: RetrievalFilters, limit: int = 20) -> list[dict]:
        where_sql, params = self._build_where_clause(filters)

        sql = f"""
        SELECT
            id,
            document_id,
            chunk_index,
            title,
            filename,
            filepath,
            source_type,
            year,
            month,
            week,
            speaker,
            seminar_date,
            content
        FROM chunks
        WHERE {where_sql}
        ORDER BY
            COALESCE(seminar_date, DATE '1900-01-01') DESC,
            year DESC NULLS LAST,
            month DESC NULLS LAST,
            week DESC NULLS LAST,
            chunk_index ASC
        LIMIT %s;
        """
        params.append(limit)

        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

        return [self._row_to_dict(row) for row in rows]

    # -----------------------------
    # 키워드 검색
    # -----------------------------
    def keyword_search(
        self,
        query: str,
        filters: RetrievalFilters | None = None,
        limit: int = 10,
    ) -> list[dict]:
        filters = filters or RetrievalFilters()
        where_sql, params = self._build_where_clause(filters)

        sql = f"""
        SELECT
            id,
            document_id,
            chunk_index,
            title,
            filename,
            filepath,
            source_type,
            year,
            month,
            week,
            speaker,
            seminar_date,
            content,
            ts_rank_cd(content_tsv, websearch_to_tsquery('simple', %s)) AS score
        FROM chunks
        WHERE {where_sql}
          AND content_tsv @@ websearch_to_tsquery('simple', %s)
        ORDER BY
            score DESC,
            COALESCE(seminar_date, DATE '1900-01-01') DESC,
            year DESC NULLS LAST,
            month DESC NULLS LAST,
            week DESC NULLS LAST,
            chunk_index ASC
        LIMIT %s;
        """

        final_params = [query] + params + [query, limit]

        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, final_params)
                rows = cur.fetchall()

        return [self._row_to_dict(row, has_score=True) for row in rows]

    # -----------------------------
    # 벡터 검색
    # -----------------------------
    def vector_search(
    self,
    query: str,
    filters: RetrievalFilters | None = None,
    limit: int = 10,
    ):
        filters = filters or RetrievalFilters()
        where_sql, params = self._build_where_clause(filters)

        query_vec = embed_query(self.model, query)

        sql = f"""
    SELECT
        id,
        document_id,
        chunk_index,
        title,
        filename,
        filepath,
        source_type,
        year,
        month,
        week,
        speaker,
        seminar_date,
        content,
        1 - (embedding <=> %s::vector) AS score
    FROM chunks
    WHERE {where_sql}
    ORDER BY embedding <=> %s::vector
    LIMIT %s;
    """

    
        final_params = [query_vec] + params + [query_vec, limit]

        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, final_params)
                rows = cur.fetchall()

        return [self._row_to_dict(row, has_score=True) for row in rows]
    #------------------------------
    # 제목 벡터 검색
    #------------------------------
    def title_vector_search(
    self,
    query: str,
    filters: RetrievalFilters | None = None,
    limit: int = 10,
    ) -> list[dict]:
        filters = filters or RetrievalFilters()
        where_sql, params = self._build_where_clause(filters)

    # documents용 WHERE로 컬럼 alias 붙이기
        doc_where_sql = (
        where_sql
        .replace("source_type", "d.source_type")
        .replace("speaker", "d.speaker")
        .replace("seminar_date", "d.seminar_date")
        .replace("year", "d.year")
        .replace("month", "d.month")
        .replace("week", "d.week")
        )

        query_vec = embed_query(self.model, query)

        sql = f"""
    SELECT
        d.id AS document_id,
        d.title,
        d.filename,
        d.filepath,
        d.source_type,
        d.year,
        d.month,
        d.week,
        d.speaker,
        d.seminar_date,
        1 - (d.title_embedding <=> %s::vector) AS score
    FROM documents d
    WHERE {doc_where_sql}
      AND d.title_embedding IS NOT NULL
    ORDER BY d.title_embedding <=> %s::vector
    LIMIT %s;
        """

        final_params = [query_vec] + params + [query_vec, limit]

        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, final_params)
                rows = cur.fetchall()
        results = []
        for row in rows:
            results.append({
            "document_id": row[0],
            "title": row[1],
            "filename": row[2],
            "filepath": row[3],
            "source_type": row[4],
            "year": row[5],
            "month": row[6],
            "week": row[7],
            "speaker": row[8],
            "seminar_date": row[9],
            "score": float(row[10]) if row[10] is not None else 0.0,
            })
        return results
    # -----------------------------
    # 하이브리드 검색
    # -----------------------------
    def hybrid_search(
    self,
    query: str,
    filters: RetrievalFilters | None = None,
    keyword_limit: int = 10,
    vector_limit: int = 10,
    title_vector_limit: int = 10,
    final_limit: int = 10,
    ) -> list[dict]:
        keyword_results = self.keyword_search(query, filters=filters, limit=keyword_limit)
        vector_results = self.vector_search(query, filters=filters, limit=vector_limit)
        title_vector_results = self.title_vector_search(query, filters=filters, limit=title_vector_limit)

        merged: dict[int, dict] = {}

        for row in keyword_results:
            doc_id = row["document_id"]
            if doc_id not in merged:
                merged[doc_id] = dict(row)
                merged[doc_id]["keyword_score"] = 0.0
                merged[doc_id]["chunk_vector_score"] = 0.0
                merged[doc_id]["title_vector_score"] = 0.0
            merged[doc_id]["keyword_score"] = max(merged[doc_id]["keyword_score"], row.get("score", 0.0))

        for row in vector_results:
            doc_id = row["document_id"]
            if doc_id not in merged:
                merged[doc_id] = dict(row)
                merged[doc_id]["keyword_score"] = 0.0
                merged[doc_id]["chunk_vector_score"] = 0.0
                merged[doc_id]["title_vector_score"] = 0.0
            merged[doc_id]["chunk_vector_score"] = max(merged[doc_id]["chunk_vector_score"], row.get("score", 0.0))

        for row in title_vector_results:
            doc_id = row["document_id"]
            if doc_id not in merged:
                merged[doc_id] = dict(row)
                merged[doc_id]["keyword_score"] = 0.0
                merged[doc_id]["chunk_vector_score"] = 0.0
                merged[doc_id]["title_vector_score"] = 0.0
            merged[doc_id]["title_vector_score"] = max(merged[doc_id]["title_vector_score"], row.get("score", 0.0))

        for row in merged.values():
            row["hybrid_score"] = (
                1.0 * row["keyword_score"]
                + 1.0 * row["chunk_vector_score"]
                + 0.1 * row["title_vector_score"]
            )

        results = list(merged.values())
        results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return results[:final_limit]

    # -----------------------------
    # 특정 문서/주차/날짜 전체 복원용
    # -----------------------------
    def get_chunks_by_document(self, document_id: int) -> list[dict]:
        sql = """
        SELECT
            id,
            document_id,
            chunk_index,
            title,
            filename,
            filepath,
            source_type,
            year,
            month,
            week,
            speaker,
            seminar_date,
            content
        FROM chunks
        WHERE document_id = %s
        ORDER BY chunk_index ASC;
        """

        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (document_id,))
                rows = cur.fetchall()

        return [self._row_to_dict(row) for row in rows]

    def get_document_text(self, document_id: int) -> str:
        chunks = self.get_chunks_by_document(document_id)
        return "\n\n".join(chunk["content"] for chunk in chunks)

    # -----------------------------
    # row 변환
    # -----------------------------
    @staticmethod
    def _row_to_dict(row, has_score: bool = False) -> dict:
        if has_score:
            return {
                "id": row[0],
                "document_id": row[1],
                "chunk_index": row[2],
                "title": row[3],
                "filename": row[4],
                "filepath": row[5],
                "source_type": row[6],
                "year": row[7],
                "month": row[8],
                "week": row[9],
                "speaker": row[10],
                "seminar_date": row[11],
                "content": row[12],
                "score": float(row[13]) if row[13] is not None else 0.0,
            }

        return {
            "id": row[0],
            "document_id": row[1],
            "chunk_index": row[2],
            "title": row[3],
            "filename": row[4],
            "filepath": row[5],
            "source_type": row[6],
            "year": row[7],
            "month": row[8],
            "week": row[9],
            "speaker": row[10],
            "seminar_date": row[11],
            "content": row[12],
        }


if __name__ == "__main__":
    retriever = Retriever()

    print("\n=== 1. 이번주 랩세미나 (필터만) ===")
    start_date, end_date = retriever.get_this_week_range()
    rows = retriever.filter_only(
        RetrievalFilters(
            source_type="lab_seminar",
            start_date=start_date,
            end_date=end_date,
        ),
        limit=10,
    )
    for r in rows[:3]:
        print(r["seminar_date"], r["title"], r["speaker"])

    print("\n=== 2. LLM 랩세미나 (하이브리드) ===")
    rows = retriever.hybrid_search(
        query="LLM 관련 세미나",
        filters=RetrievalFilters(source_type="lab_seminar"),
        final_limit=5,
    )
    for r in rows:
        print(r["hybrid_score"], r["title"], r["seminar_date"])

    print("\n=== 3. 2020년 8월 2주차 STM32 (하이브리드) ===")
    rows = retriever.hybrid_search(
        query="STM32",
        filters=RetrievalFilters(
            source_type="weekly_report",
            year=2020,
            month=8,
            week=2,
        ),
        final_limit=5,
    )
    for r in rows:
        print(r["hybrid_score"], r["title"], r["year"], r["month"], r["week"])

    print("\n=== 4. 특정 주차 전체 텍스트 복원 ===")
    rows = retriever.filter_only(
        RetrievalFilters(source_type="weekly_report", year=2020, month=8, week=2),
        limit=5,
    )
    if rows:
        doc_id = rows[0]["document_id"]
        full_text = retriever.get_document_text(doc_id)
        print(full_text[:1000])