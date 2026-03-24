# BL-BE-10

**Backlog Type**
Behavior Backlog

**Backlog Title**
종목 시장(미국/한국)에 따라 복수 뉴스 소스를 조합하여 검색한다

**배경**
현재 뉴스 검색은 SerpAPI 단일 소스에만 의존하며 무료 플랜 한도(100회/월)가 너무 낮다.
미국 종목은 Finnhub을 병행하고, 한국 종목은 네이버 뉴스를 병행하여 뉴스 다양성과 검색 한도를 개선한다.

**Success Criteria**
- `GET /news/search?keyword=CXAI&market=US` 요청 시 SerpAPI + Finnhub 결과를 합산하여 반환한다
- `GET /news/search?keyword=헥토파이낸셜&market=KR` 요청 시 SerpAPI + 네이버 뉴스 결과를 합산하여 반환한다
- `market` 파라미터를 생략하면 기존 SerpAPI 단일 소스로 동작한다 (하위 호환)
- 각 소스에서 가져온 결과는 `published_at` 기준 최신순으로 정렬하여 반환한다
- 중복 기사(동일 URL)는 제거한다
- 개별 소스에서 오류가 발생해도 나머지 소스의 결과는 정상 반환한다 (Partial Success)

**응답 형식**
기존 `SearchNewsResponse` 형식 유지:
```json
{
  "items": [
    {
      "title": "CXApp Launches AI-Powered Platform...",
      "snippet": "...",
      "source": "Yahoo",
      "published_at": "2026-03-17",
      "link": "https://..."
    }
  ],
  "total_count": 12,
  "page": 1,
  "page_size": 10
}
```

**구현 범위**

### 1. settings.py — Finnhub API 키 추가
- `finnhub_api_key: str = ""` 필드 추가

### 2. FinnhubNewsSearchAdapter (신규)
- 위치: `adapter/outbound/external/finnhub_news_search_adapter.py`
- `NewsSearchPort` 구현
- `GET https://finnhub.io/api/v1/company-news?symbol={keyword}&from=...&to=...&token=...`
- 반환: `List[NewsArticle]`

### 3. NaverNewsSearchAdapter (신규)
- 위치: `adapter/outbound/external/naver_news_search_adapter.py`
- `NewsSearchPort` 구현
- `https://search.naver.com/search.naver?where=news&query={keyword}` HTML 파싱
- title: `"title":"..."` JSON 패턴 regex 추출
- url: `n.news.naver.com` href regex 추출
- 반환: `List[NewsArticle]`

### 4. CompositeNewsSearchAdapter (신규)
- 위치: `adapter/outbound/external/composite_news_search_adapter.py`
- `NewsSearchPort` 구현
- 생성자: `adapters: List[NewsSearchPort]` 주입
- 각 어댑터를 순차 호출, 결과 합산
- 중복 URL 제거 후 `published_at` 기준 정렬
- 개별 어댑터 오류 시 로그 기록 후 계속 진행 (Partial Success)

### 5. SearchNewsRequest 수정
- `market: Optional[str] = None` 필드 추가 (`"US"` | `"KR"` | `None`)

### 6. news_search_router.py 수정
- `market` 쿼리 파라미터 수신
- market 값에 따라 Composite 어댑터 조합 선택:
  - `US` → `[SerpNewsSearchAdapter, FinnhubNewsSearchAdapter]`
  - `KR` → `[SerpNewsSearchAdapter, NaverNewsSearchAdapter]`
  - `None` → `[SerpNewsSearchAdapter]` (기존 동작)

**Todo**
1. `settings.py`에 `finnhub_api_key` 필드를 추가한다
2. `FinnhubNewsSearchAdapter`를 구현한다
3. `NaverNewsSearchAdapter`를 구현한다
4. `CompositeNewsSearchAdapter`를 구현한다
5. `SearchNewsRequest`에 `market` 필드를 추가한다
6. `news_search_router.py`에서 market에 따라 어댑터를 조합하여 주입한다
7. `.env.example`에 `FINNHUB_API_KEY=` 항목을 추가한다 (있는 경우)
