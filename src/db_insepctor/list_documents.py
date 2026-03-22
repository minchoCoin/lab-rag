import argparse
from db import connect_db


def list_documents(source_type=None, limit=100, offset=0):
    where = ["1=1"]
    params = []

    if source_type:
        where.append("source_type = %s")
        params.append(source_type)

    where_sql = " AND ".join(where)

    sql = f"""
    SELECT
        id,
        source_type,
        title,
        filename,
        year,
        month,
        week,
        speaker,
        seminar_date
    FROM documents
    WHERE {where_sql}
    ORDER BY id DESC
    LIMIT %s OFFSET %s;
    """

    params.extend([limit, offset])

    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

    for row in rows:
        print("=" * 80)
        print(f"id            : {row[0]}")
        print(f"type          : {row[1]}")
        print(f"title         : {row[2]}")
        print(f"filename      : {row[3]}")
        print(f"year/month/wk : {row[4]} / {row[5]} / {row[6]}")
        print(f"speaker       : {row[7]}")
        print(f"date          : {row[8]}")


def main():
    parser = argparse.ArgumentParser(description="List documents")

    parser.add_argument("--source-type", choices=["lab_seminar", "weekly_report"])
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)

    args = parser.parse_args()

    list_documents(
        source_type=args.source_type,
        limit=args.limit,
        offset=args.offset,
    )


if __name__ == "__main__":
    main()

'''
# 전체 문서
python list_documents.py

# 랩세미나만
python list_documents.py --source-type lab_seminar

# 페이징
python list_documents.py --limit 20 --offset 20
'''