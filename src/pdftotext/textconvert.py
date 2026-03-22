import os
import subprocess

SRC_ROOTS = [
    "pdf/Lab seminar",
    "pdf/weekly report"
]

DST_ROOTS = [
    "text/Lab seminar",
    "text/weekly report"
]


def clean_formfeed(txt_path):
    try:
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        # \f → \n 치환
        text = text.replace("\f", "\n")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

    except Exception as e:
        print(f"[WARN] f->n 변환 실패: {txt_path} ({e})")


def convert_pdf_to_text(src_path, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(src_path))[0]
    txt_path = os.path.join(dst_dir, base_name + ".txt")

    if os.path.exists(txt_path):
        return

    cmd = [
        "pdftotext",
        "-layout",
        src_path,
        txt_path
    ]

    try:
        subprocess.run(cmd, check=True)
        
        
        clean_formfeed(txt_path)

        print(f"[OK] {src_path} -> {txt_path}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {src_path} 변환 실패: {e}")


def process_root(src_root, dst_root):
    for root, dirs, files in os.walk(src_root):
        for file in files:
            if file.lower().endswith(".pdf"):
                src_file = os.path.join(root, file)

                rel_path = os.path.relpath(root, src_root)
                dst_dir = os.path.join(dst_root, rel_path)

                convert_pdf_to_text(src_file, dst_dir)


def main():
    for src_root, dst_root in zip(SRC_ROOTS, DST_ROOTS):
        process_root(src_root, dst_root)


if __name__ == "__main__":
    main()