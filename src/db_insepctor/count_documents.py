import argparse
from db import connect_db


def count_documents(source_type=None):
    where = ["1=1"]
    params = []

    if source_type:
        where.append("source_type = %s")
        params.append(source_type)

    where_sql = " AND ".join(where)

    sql = f"""
    SELECT COUNT(*) FROM documents
    WHERE {where_sql};
    """

    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()[0]


def count_chunks(source_type=None):
    where = ["1=1"]
    params = []

    if source_type:
        where.append("source_type = %s")
        params.append(source_type)

    where_sql = " AND ".join(where)

    sql = f"""
    SELECT COUNT(*) FROM chunks
    WHERE {where_sql};
    """

    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()[0]


def count_documents_by_type():
    sql = """
    SELECT source_type, COUNT(*)
    FROM documents
    GROUP BY source_type;
    """

    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()


def main():
    parser = argparse.ArgumentParser(description="Count documents and chunks")

    parser.add_argument("--source-type", choices=["lab_seminar", "weekly_report"])
    parser.add_argument("--detail", action="store_true", help="show per-type breakdown")

    args = parser.parse_args()

    total_docs = count_documents(source_type=args.source_type)
    total_chunks = count_chunks(source_type=args.source_type)

    print("=" * 60)
    print("📊 DB 통계")
    print("=" * 60)

    if args.source_type:
        print(f"source_type : {args.source_type}")

    print(f"문서 수      : {total_docs}")
    print(f"chunk 수     : {total_chunks}")

    if total_docs > 0:
        print(f"문서당 chunk : {total_chunks / total_docs:.2f}")

    if args.detail:
        print("\n📌 타입별 문서 수")
        rows = count_documents_by_type()
        for source_type, count in rows:
            print(f"{source_type:15} : {count}")


if __name__ == "__main__":
    main()