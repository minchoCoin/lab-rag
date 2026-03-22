import os
import re
from collections import defaultdict

SRC_ROOT = "text/weekly report"
DST_ROOT = "text/weekly report by week"

# "8월 2주차 페이지 1" 또는 "2주차 페이지 1"
PAGE_MARKER_RE = re.compile(
    r'^\s*((?:\d{1,2}월\s*)?[1-5]주차)\s+페이지\s+\d+\s*$',
    re.MULTILINE
)


MONTH_RE = re.compile(r'(\d{1,2}월)')


def normalize_text(text: str) -> str:
    text = text.replace("\f", "\n")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def extract_month_from_filename(filename: str) -> str | None:
    m = MONTH_RE.search(filename)
    return m.group(1) if m else None


def normalize_week_label(week_label: str, file_month: str | None) -> str:
    week_label = re.sub(r'\s+', ' ', week_label.strip())

    # 이미 "8월 2주차" 형태면 그대로 사용
    if "월" in week_label:
        return week_label

    # "2주차" 형태면 파일명에서 찾은 월 정보 붙이기
    if file_month:
        return f"{file_month} {week_label}"

    return week_label


def split_weekly_report_by_week(text: str, file_month: str | None = None) -> dict[str, str]:
    text = normalize_text(text)

    matches = list(PAGE_MARKER_RE.finditer(text))
    week_to_pages = defaultdict(list)

    if not matches:
        return {}

    prev_end = 0
    for m in matches:
        raw_week_label = m.group(1).strip()
        week_label = normalize_week_label(raw_week_label, file_month)

        page_content = text[prev_end:m.start()].strip()
        if page_content:
            week_to_pages[week_label].append(page_content)

        prev_end = m.end()

    tail = text[prev_end:].strip()
    if tail:
        last_raw_week_label = matches[-1].group(1).strip()
        last_week_label = normalize_week_label(last_raw_week_label, file_month)
        week_to_pages[last_week_label].append(tail)

    week_to_text = {}
    for week_label, pages in week_to_pages.items():
        combined = "\n\n".join(p.strip() for p in pages if p.strip()).strip()
        if combined:
            week_to_text[week_label] = combined

    return week_to_text


def save_week_splits(src_path: str, dst_dir: str):
    os.makedirs(dst_dir, exist_ok=True)

    with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    base_name = os.path.splitext(os.path.basename(src_path))[0]
    file_month = extract_month_from_filename(base_name)

    week_to_text = split_weekly_report_by_week(text, file_month=file_month)

    if not week_to_text:
        print(f"[WARN] 주차 마커를 찾지 못함: {src_path}")
        return

    for week_label, week_text in sorted(week_to_text.items()):
        safe_week_label = week_label.replace(" ", "_")
        out_path = os.path.join(dst_dir, f"{base_name}_{safe_week_label}.txt")
        if os.path.exists(out_path):
            #print(f"[SKIP] 이미 존재: {out_path}")
            continue
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(week_text + "\n")

        print(f"[OK] {src_path} -> {out_path}")


def main():
    for root, dirs, files in os.walk(SRC_ROOT):
        for file in files:
            if not file.lower().endswith(".txt"):
                continue

            src_path = os.path.join(root, file)

            rel_path = os.path.relpath(root, SRC_ROOT)
            dst_dir = os.path.join(DST_ROOT, rel_path)

            save_week_splits(src_path, dst_dir)


if __name__ == "__main__":
    main()