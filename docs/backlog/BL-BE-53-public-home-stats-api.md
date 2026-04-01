# BL-BE-53

**Backlog Type**
Feature / public / home-stats

**Backlog Title**
공개 홈 통계 API — 공개 관심종목 기반 센티먼트 집계 엔드포인트

**Success Criteria**
- `GET /public/home-stats` 엔드포인트가 인증 없이 호출 가능하다
- `is_watchlist_public = True` 인 사용자들의 관심종목 심볼을 수집한다
- 대표 종목(삼성전자 005930, SK하이닉스 000660)을 기본 포함한다
- 성능을 위해 최대 20개 심볼로 제한한다
- 응답 형식은 `List[AnalysisLogResponse]` 로, FE 셀렉터(`calcHomeStats`, `calcTodayBriefing`)와 호환된다

**Todo**
1. [x] `public_router.py` 에 `GET /public/home-stats` 엔드포인트 추가
2. [x] `AccountORM` 에서 `is_watchlist_public = True` 인 account_id 목록 조회
3. [x] `WatchlistItemORM` 에서 해당 account들의 symbol 수집 후 대표 종목과 합산
4. [x] 최대 20개 심볼로 슬라이싱 후 `find_latest_by_symbols` 호출
5. [x] `AnalysisLogResponse` 형식으로 반환

**관련**
- [BL-FE-57](../../alpha-desk-frontend/docs/backlog/BL-FE-57-home-public-stats-display.md) — FE 홈 공개 데이터 표시

**개정 이력**
- 2026-03-31: 초안 및 구현
