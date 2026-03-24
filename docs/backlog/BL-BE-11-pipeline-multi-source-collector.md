# BL-BE-11

**Backlog Type**
Behavior Backlog

**Backlog Title**
파이프라인이 종목 시장(미국/한국)에 따라 Finnhub 또는 네이버 뉴스를 추가로 수집한다

**배경**
현재 파이프라인은 SerpAPI 단일 소스(`NewsCollectorAdapter`)만 사용한다.
미국 종목은 Finnhub, 한국 종목은 네이버 뉴스를 별도 Collector로 추가하여
수집 다양성을 높이고 SerpAPI 한도 의존도를 줄인다.

**Success Criteria**
- 파이프라인 실행 시 6자리 숫자 종목코드(KR)는 `NaverNewsCollectorAdapter`가 추가로 수집한다
- 영문 종목코드(US)는 `FinnhubCollectorAdapter`가 추가로 수집한다
- 각 Collector는 `CollectorPort`를 구현한다
- 개별 Collector에서 오류가 발생해도 나머지 Collector 수집 결과는 정상 반환한다
- 기존 `NewsCollectorAdapter`, `DartCollectorAdapter` 동작은 변경하지 않는다

**구현 범위**

### 1. FinnhubCollectorAdapter (신규)
- 위치: `adapter/outbound/external/finnhub_collector_adapter.py`
- `CollectorPort` 구현
- 영문 종목코드(US)만 처리 — 6자리 숫자이면 빈 리스트 반환
- `GET https://finnhub.io/api/v1/company-news?symbol={symbol}&from=...&to=...`
- `RawArticle` 변환: `source_type="NEWS"`, `source_name="FINNHUB"`, `lang="en"`

### 2. NaverNewsCollectorAdapter (신규)
- 위치: `adapter/outbound/external/naver_news_collector_adapter.py`
- `CollectorPort` 구현
- 6자리 숫자 종목코드(KR)만 처리 — 영문 코드이면 빈 리스트 반환
- `SYMBOL_TO_NAME` 매핑으로 종목명 변환 후 네이버 뉴스 검색
- `https://search.naver.com/search.naver?where=news&query={종목명}` HTML 파싱
- title: `"title":"..."` regex 추출 / url: `n.news.naver.com` href regex 추출
- `RawArticle` 변환: `source_type="NEWS"`, `source_name="NAVER_NEWS"`, `lang="ko"`

### 3. pipeline_router.py 수정
- `collectors` 리스트에 `FinnhubCollectorAdapter`, `NaverNewsCollectorAdapter` 추가
```python
collectors=[
    DartCollectorAdapter(),
    NewsCollectorAdapter(),
    FinnhubCollectorAdapter(),
    NaverNewsCollectorAdapter(),
]
```

**Todo**
1. `FinnhubCollectorAdapter`를 구현한다
2. `NaverNewsCollectorAdapter`를 구현한다
3. `pipeline_router.py`의 `collectors` 리스트에 두 어댑터를 추가한다
