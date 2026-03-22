import argparse
from db import connect_db


def delete_document(document_id: int, force: bool = False):
    with connect_db() as conn:
        with conn.cursor() as cur:

            # 먼저 확인
            cur.execute("""
                SELECT id, title, filename
                FROM documents
                WHERE id = %s;
            """, (document_id,))
            row = cur.fetchone()

            if not row:
                print(f"[ERROR] document_id={document_id} not found")
                return

            print("삭제 대상:")
            print(f"id       : {row[0]}")
            print(f"title    : {row[1]}")
            print(f"filename : {row[2]}")

            if not force:
                confirm = input("정말 삭제하시겠습니까? (y/N): ")
                if confirm.lower() != "y":
                    print("취소됨")
                    return

            # 삭제
            cur.execute("""
                DELETE FROM documents
                WHERE id = %s;
            """, (document_id,))

        conn.commit()

    print(f"[OK] document_id={document_id} 삭제 완료")


def main():
    parser = argparse.ArgumentParser(description="Delete document by id")

    parser.add_argument("--id", type=int, required=True, help="document id")
    parser.add_argument("--force", action="store_true", help="skip confirmation")

    args = parser.parse_args()

    delete_document(args.id, force=args.force)


if __name__ == "__main__":
    main()

'''
# 삭제 (확인 있음)
python delete_document.py --id 5

# 강제 삭제
python delete_document.py --id 5 --force
'''