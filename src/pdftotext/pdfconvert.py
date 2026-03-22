import os
import subprocess


SRC_ROOT = "origin/Lab seminar"
DST_ROOT = "pdf/Lab seminar"

def convert_pptx_to_pdf(src_path, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)

    
    base_name = os.path.splitext(os.path.basename(src_path))[0]
    pdf_path = os.path.join(dst_dir, base_name + ".pdf")

    
    if os.path.exists(pdf_path):
        
        return

    cmd = [
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", dst_dir,
        src_path
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"[OK] {src_path} -> {pdf_path}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {src_path} 변환 실패: {e}")


def main():
    for root, dirs, files in os.walk(SRC_ROOT):
        for file in files:
            if file.lower().endswith(".pptx"):
                src_file = os.path.join(root, file)

                
                rel_path = os.path.relpath(root, SRC_ROOT)
                dst_dir = os.path.join(DST_ROOT, rel_path)

                convert_pptx_to_pdf(src_file, dst_dir)


if __name__ == "__main__":
    main()