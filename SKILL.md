---
name: ESLAB-TEAMS
description: "ESLAB 주간 보고서 및 랩세미나 요약"
---

# conda 환경 사용법
```bash
#!/bin/bash

export TRITON_PTXAS_PATH=/usr/local/cuda/bin/ptxas
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:${LD_LIBRARY_PATH:-}

source ~/anaconda3/etc/profile.d/conda.sh
```

# conda 환경 활성화
```bash
conda activate labrag
```

만약 위 코드가 에러가 난다면 다음 파이썬을 사용하라
```bash
/home/eslab/anaconda3/envs/labrag/bin/python 
```

# 파일 위치
주의: 아래 파일을 실행하기 전 labrag conda 환경을 활성화하여야한다.

`/home/eslab/eslab_teams/retriever_wrapper.py`

즉
```bash
/home/eslab/anaconda3/envs/labrag/bin/python  /home/eslab/eslab_teams/retriever_wrapper.py
```


# 사용자의 주간 보고서 및 랩 세미나 관련 질문 처리 방법

1. 위의 conda 환경 사용법과 환경 활성화 방법을 사용하여 conda 환경을 활성화한다.
2. retriever_wrapper.py 파일을 실행하여 사용자 질문과 관련된 주간 보고서 및 랩 세미나 질문을 처리한다.

retriever_wrapper.py 파일 사용법은 다음과 같다.

## retriever_wrapper.py
```bash
usage: retriever_wrapper.py [-h] {filter,keyword,vector,hybrid,document} ...

Retriever CLI wrapper for metadata / keyword / vector / hybrid search

positional arguments:
  {filter,keyword,vector,hybrid,document}
    filter              Metadata-only retrieval
    keyword             Keyword search with optional filters
    vector              Vector search with optional filters
    hybrid              Hybrid search with optional filters
    document            Get full document text by document_id

options:
  -h, --help            show this help message and exit
```

### filter
filter는 검색 키워드없이 날짜 등으로 검색할 때 필요한 것이다.
```bash
usage: retriever_wrapper.py filter [-h] [--source-type {lab_seminar,weekly_report}] [--speaker SPEAKER] [--seminar-date SEMINAR_DATE] [--start-date START_DATE] [--end-date END_DATE]
                                   [--year YEAR] [--month MONTH] [--week WEEK] [--limit LIMIT]

options:
  -h, --help            show this help message and exit
  --source-type {lab_seminar,weekly_report}
  --speaker SPEAKER
  --seminar-date SEMINAR_DATE
                        YYYY-MM-DD
  --start-date START_DATE
                        YYYY-MM-DD
  --end-date END_DATE   YYYY-MM-DD
  --year YEAR
  --month MONTH
  --week WEEK
  --limit LIMIT
  --filepath-keyword FILEPATH_KEYWORD filepath에 포함되어야 하는 키워드 'lab 세미나', 교육, 졸업 이 있을 수 있다.
```

### keyword
keyword는 검색 키워드를 벡터화 없이 그대로 검색할 때 사용하는 것이다. 가급적 이것말고, hybrid를 사용하라
```bash
usage: retriever_wrapper.py keyword [-h] --query QUERY [--source-type {lab_seminar,weekly_report}] [--speaker SPEAKER] [--seminar-date SEMINAR_DATE] [--start-date START_DATE]
                                    [--end-date END_DATE] [--year YEAR] [--month MONTH] [--week WEEK] [--limit LIMIT]

options:
  -h, --help            show this help message and exit
  --query QUERY
  --source-type {lab_seminar,weekly_report}
  --speaker SPEAKER
  --seminar-date SEMINAR_DATE
                        YYYY-MM-DD
  --start-date START_DATE
                        YYYY-MM-DD
  --end-date END_DATE   YYYY-MM-DD
  --year YEAR
  --month MONTH
  --week WEEK
  --limit LIMIT
  --filepath-keyword FILEPATH_KEYWORD filepath에 포함되어야 하는 키워드 'lab 세미나', 교육, 졸업 이 있을 수 있다.
```

### vector
vector는 검색 키워드를 벡터화하여 DB에서 유사한 것을 검색할 때 사용한다.
```bash
usage: retriever_wrapper.py vector [-h] --query QUERY [--source-type {lab_seminar,weekly_report}] [--speaker SPEAKER] [--seminar-date SEMINAR_DATE] [--start-date START_DATE]
                                   [--end-date END_DATE] [--year YEAR] [--month MONTH] [--week WEEK] [--limit LIMIT]

options:
  -h, --help            show this help message and exit
  --query QUERY
  --source-type {lab_seminar,weekly_report}
  --speaker SPEAKER
  --seminar-date SEMINAR_DATE
                        YYYY-MM-DD
  --start-date START_DATE
                        YYYY-MM-DD
  --end-date END_DATE   YYYY-MM-DD
  --year YEAR
  --month MONTH
  --week WEEK
  --limit LIMIT
  --filepath-keyword FILEPATH_KEYWORD filepath에 포함되어야 하는 키워드 'lab 세미나', 교육, 졸업 이 있을 수 있다.
```

### title vector
특히 랩세미나에서, 랩세미나 발표 pdf 제목을 기준으로 검색할 때 사용한다.

```
usage: retriever_wrapper.py title-vector [-h] --query QUERY [--source-type {lab_seminar,weekly_report}] [--speaker SPEAKER] [--seminar-date SEMINAR_DATE] [--start-date START_DATE]
                                         [--end-date END_DATE] [--year YEAR] [--month MONTH] [--week WEEK] [--limit LIMIT] [--filepath-keyword FILEPATH_KEYWORD]

options:
  -h, --help            show this help message and exit
  --query QUERY
  --source-type {lab_seminar,weekly_report}
  --speaker SPEAKER
  --seminar-date SEMINAR_DATE
                        YYYY-MM-DD
  --start-date START_DATE
                        YYYY-MM-DD
  --end-date END_DATE   YYYY-MM-DD
  --year YEAR
  --month MONTH
  --week WEEK
  --limit LIMIT
  --filepath-keyword FILEPATH_KEYWORD filepath에 포함되어야 하는 키워드 'lab 세미나', 교육, 졸업 이 있을 수 있다.
```

랩세미나에서 LLM과 관련된 제목을 가진 문서를 검색할 경우:

```bash
python retriever_wrapper.py title-vector \
  --query "LLM" \
  --source-type lab_seminar \
  --limit 10
```

2026년에 진행된 LLM과 관련된 랩세미나 문서를 검색할 경우: 

```bash
python retriever_wrapper.py title-vector \
  --query "large language model" \
  --source-type lab_seminar \
  --year 2026 \
  --limit 10
```

### hybrid
hybrid는 검색 키워드를 그대로 및 벡터화하여 DB에서 유사한 것을 검색할 때 사용된다.
```bash
usage: retriever_wrapper.py hybrid [-h] --query QUERY [--source-type {lab_seminar,weekly_report}] [--speaker SPEAKER] [--seminar-date SEMINAR_DATE] [--start-date START_DATE]
                                   [--end-date END_DATE] [--year YEAR] [--month MONTH] [--week WEEK] [--limit LIMIT] [--keyword-limit KEYWORD_LIMIT] [--vector-limit VECTOR_LIMIT]

options:
  -h, --help            show this help message and exit
  --query QUERY
  --source-type {lab_seminar,weekly_report}
  --speaker SPEAKER
  --seminar-date SEMINAR_DATE
                        YYYY-MM-DD
  --start-date START_DATE
                        YYYY-MM-DD
  --end-date END_DATE   YYYY-MM-DD
  --year YEAR
  --month MONTH
  --week WEEK
  --limit LIMIT
  --keyword-limit KEYWORD_LIMIT
  --vector-limit VECTOR_LIMIT
  --filepath-keyword FILEPATH_KEYWORD filepath에 포함되어야 하는 키워드 'lab 세미나', 교육, 졸업 이 있을 수 있다.
```


### document
document는 위의 keyword, vector, hybrid를 바탕으로 검색된 문서들 중 특정 문서 전체를 보고 싶을 때 문서 ID를 사용하여 문서 전체를 보는 것이다.
```
usage: retriever_wrapper.py document [-h] --document-id DOCUMENT_ID

options:
  -h, --help            show this help message and exit
  --document-id DOCUMENT_ID
```

### 검색 시 유의점
랩 세미나의 경우 week는 항상 null이다.

주간 보고의 경우 seminar_data는 항상 null이다.

주간 보고의 speaker 란은 부정확할 수도 있다.

### 출력 포맷 (랩 세미나)
```
[
  {
    "id": 17,
    "document_id": 5,
    "chunk_index": 0,
    "title": "LLM survey",
    "filename": "[20190118_홍길동] LLM survey.txt",
    "filepath": "text/Lab seminar/[20190118_홍길동] LLM survey.txt",
    "source_type": "lab_seminar",
    "year": 2019,
    "month": 1,
    "week": null,
    "speaker": "홍길동",
    "seminar_date": "2019-01-18",
    "content": "...",
    "score": 0.8123,
    "keyword_score": 0.0,
    "chunk_vector_score": 0.0,
    "title_vector_score": 0.45040685985149853,
    "hybrid_score": 0.0
  }
]
```
단, filter 검색의 경우 score란은 없다.

### 출력 포맷 (주간 보고)
```
[
  {
    "id": 12856,
    "document_id": 972,
    "chunk_index": 0,
    "title": "2026년 3월 주간보고_3월_1주차",
    "filename": "2026년 3월 주간보고_3월_1주차.txt",
    "filepath": "text/weekly report by week/2026년 주간보고/2026년 3월 주간보고_3월_1주차.txt",
    "source_type": "weekly_report",
    "year": 2026,
    "month": 3,
    "week": 1,
    "speaker": 홍길동,
    "seminar_date": null,
    "content": "...",
    "score": 0.8123,
    "keyword_score": 0.0,
    "chunk_vector_score": 0.0,
    "title_vector_score": 0.45040685985149853,
    "hybrid_score": 0.0
  }
]
```
단, filter 검색의 경우 score란은 없다.

주간보고는 speaker 별로 청크가 나누어져있음.


### 사용 예시

#### 예시 1: 날짜 범위 랩 세미나 조회

이번 주의 날짜를 확인하여, filter를 사용하여 확인

예시 입력

```bash
python retriever_wrapper.py filter \
  --source-type lab_seminar \
  --start-date 2026-03-16 \
  --end-date 2026-03-22 \
  --limit 20
```

#### 예시 2: 랩 세미나 키워드 검색(하이브리드 추천)
```bash
python retriever_wrapper.py hybrid \
  --query "대형 언어 모델 관련 세미나" \
  --source-type lab_seminar \
  --limit 5 \
  --keyword-limit 10 \
  --vector-limit 10
```

#### 예시 3: 특정 날짜 랩세미나 조회
```bash
python retriever_wrapper.py filter \
  --source-type lab_seminar \
  --seminar-date 2026-03-13 \
  --limit 20
```

#### 예시 5: 특정 사람 랩세미나 조회
```bash
python retriever_wrapper.py filter \
  --source-type lab_seminar \
  --speaker "홍길동" \
  --limit 20
```

#### 예시 6: 특정 랩세미나 문서 전체 조회
```bash
python retriever_wrapper.py document --document-id 123
```

#### 예시 7: 이번 주 주간 보고
이번 주가 몇월 몇째주인지 파악하여 year month week를 채워 filter로 검색한다.
```bash
python retrieve_wrapper.py filter \
  --source-type weekly_report \
  --year 2026 \
  --month 3 \
  --week 3 \
  --limit 20
```

#### 예시 8: 특정 주 주간 보고
```bash
python retrieve_wrapper.py filter \
  --source-type weekly_report \
  --year 2020 \
  --month 8 \
  --week 2 \
  --limit 20
```

#### 예시 9: 특정 사람 주간 보고
```bash
python retrieve_wrapper.py filter \
  --source-type weekly_report \
  --speaker "홍길동" \
  --limit 20
```

#### 예시 10: 전체 주간 보고에서 하이브리드 검색
```bash
python retrieve_wrapper.py hybrid \
  --query "STM32" \
  --source-type weekly_report \
  --limit 10 \
  --keyword-limit 10 \
  --vector-limit 10
```

#### 예시 11: 특정 주차 안에서 하이브리드 검색
```bash
python retrieve_wrapper.py hybrid \
  --query "STM32" \
  --source-type weekly_report \
  --year 2020 \
  --month 8 \
  --week 2 \
  --limit 10 \
  --keyword-limit 10 \
  --vector-limit 10
```

#### 예시 11: 특정 월 안에서 하이브리드 검색
```bash
python retrieve_wrapper.py hybrid \
  --query "STM32" \
  --source-type weekly_report \
  --year 2020 \
  --month 8 \
  --limit 10 \
  --keyword-limit 10 \
  --vector-limit 10
```

#### 예시 12: 특정 사람 안에서 하이브리드 검색
```bash
python retrieve_wrapper.py hybrid \
  --query "LLM" \
  --source-type weekly_report \
  --speaker "홍길동" \
  --limit 10 \
  --keyword-limit 10 \
  --vector-limit 10
```

#### 예시 13: 특정 주간 보고 문서 전체 조회
```bash
python retriever_wrapper.py document --document-id 123
```

#### 예시 14: 랩세미나 검색 시 홍길동이 진행한 '기술세미나'만 조회
```bash
python retriever_wrapper.py filter \
  --source-type lab_seminar \
  --speaker "홍길동" \
  --limit 20
  --filepath-keyword 'lab 세미나'
```

#### 예시 14: 랩세미나 검색 시 홍길동이 진행한 '교육세미나'만 조회
```bash
python retriever_wrapper.py filter \
  --source-type lab_seminar \
  --speaker "홍길동" \
  --limit 20
  --filepath-keyword '교육'
```

#### 예시 14: 랩세미나 검색 시 홍길동이 진행한 '졸업 논문 세미나'만 조회
```bash
python retriever_wrapper.py filter \
  --source-type lab_seminar \
  --speaker "홍길동" \
  --limit 20
  --filepath-keyword '졸업'
```



# 주의
주간 보고에서 speaker는 부정확할 수 있어, 필히 전체 document를 확인하라

그리고 답을 할 때, 검색된 문서를 기준으로만 대답하라!