import re
from pathlib import Path
from typing import Iterator
from typing import Optional
from config import CHUNK_SIZE, CHUNK_OVERLAP

YEAR_RE = re.compile(r"(\d{4})년")
MONTH_RE = re.compile(r"(\d{1,2})월")
WEEK_RE = re.compile(r"([1-5])주차")
LAB_SEMINAR_RE = re.compile(r'^\[(\d{8})_([^\]]+)\]\s*(.+)$')


def clean_text(text: str) -> str:
    text = text.replace("\f", "\n")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    text = clean_text(text)
    if not text:
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end].strip()

        if end < text_len:
            last_break = chunk.rfind("\n")
            if last_break > chunk_size * 0.5:
                chunk = chunk[:last_break].strip()
                end = start + last_break

        if chunk:
            chunks.append(chunk)

        if end >= text_len:
            break

        start = max(end - overlap, start + 1)

    return chunks


def iter_txt_files(root: str) -> Iterator[Path]:
    for path in Path(root).rglob("*.txt"):
        if path.is_file():
            yield path


def parse_metadata(path: Path, source_type: str) -> dict:
    stem = path.stem
    full_path_str = str(path).replace("\\", "/")

    year = None
    month = None
    week = None
    speaker = None
    seminar_date = None
    title = stem

    if source_type == "lab_seminar":
        m = LAB_SEMINAR_RE.match(stem)
        if m:
            raw_date, speaker, raw_title = m.groups()
            year = int(raw_date[:4])
            month = int(raw_date[4:6])
            seminar_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
            title = raw_title.strip()
        else:
            year_match = YEAR_RE.search(stem) or YEAR_RE.search(full_path_str)
            month_match = MONTH_RE.search(stem) or MONTH_RE.search(full_path_str)

            year = int(year_match.group(1)) if year_match else None
            month = int(month_match.group(1)) if month_match else None

    elif source_type == "weekly_report":
        year_match = YEAR_RE.search(stem) or YEAR_RE.search(full_path_str)
        month_match = MONTH_RE.search(stem) or MONTH_RE.search(full_path_str)
        week_match = WEEK_RE.search(stem)

        year = int(year_match.group(1)) if year_match else None
        month = int(month_match.group(1)) if month_match else None
        week = int(week_match.group(1)) if week_match else None

    return {
        "source_type": source_type,
        "title": title,
        "filename": path.name,
        "filepath": full_path_str,
        "year": year,
        "month": month,
        "week": week,
        "speaker": speaker,
        "seminar_date": seminar_date,
    }


NAME_RE = re.compile(r"^[가-힣]{2,5}$|^[A-Za-z][A-Za-z .'-]{1,30}$")
DATE_RE = re.compile(
    r"^\s*\d{4}년\s*\d{1,2}월\s*\d{1,2}일\s*"
    r"(월요일|화요일|수요일|목요일|금요일|토요일|일요일)?\s*"
    r"(오전|오후)?\s*\d{1,2}:\d{2}\s*$"
)

SECTION_RE = re.compile(r"^\s*(지난\s*주\s*업무|이번\s*주\s*업무|다음\s*주\s*업무)\s*$")


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def is_name_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False

    # 불릿/섹션/기타 잡음 제외
    banned_tokens = ["•", "○", "▪", "-", ":", "/", "(", ")", "[", "]"]
    if any(tok in s for tok in banned_tokens):
        return False

    if SECTION_RE.fullmatch(s):
        return False

    # 너무 긴 일반 문장 제외
    if len(s) > 30:
        return False

    return bool(NAME_RE.fullmatch(s))


def is_date_line(line: str) -> bool:
    return bool(DATE_RE.fullmatch(line.strip()))


def split_by_speaker(text: str) -> list[tuple[Optional[str], str]]:
    """
    사람별 블록 분리.
    기준:
      [이름 줄]
      [날짜 줄]
    이 연속으로 나오면 새 speaker 시작으로 판단한다.

    반환:
      [
        ("홍길동", "2026년 ...\n\n지난 주 업무\n..."),
        ("이순신", "2026년 ...\n\n지난 주 업무\n..."),
      ]

    어떤 speaker도 못 찾으면 [(None, 전체텍스트)] 반환
    """
    text = clean_text(text)
    lines = text.split("\n")

    # 사람 시작 인덱스 찾기
    starts: list[tuple[int, str]] = []
    for i in range(len(lines) - 1):
        line = lines[i].strip()
        next_line = lines[i + 1].strip()

        if is_name_line(line) and is_date_line(next_line):
            starts.append((i, line))

    if not starts:
        return [(None, text)]

    blocks: list[tuple[Optional[str], str]] = []

    for idx, (start_i, speaker) in enumerate(starts):
        end_i = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        block_text = "\n".join(lines[start_i + 1:end_i]).strip()  # 날짜부터 포함
        blocks.append((speaker, block_text))

    return blocks

