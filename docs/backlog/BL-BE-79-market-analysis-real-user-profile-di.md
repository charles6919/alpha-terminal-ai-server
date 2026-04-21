# BL-BE-79: market_analysis_router MockUserProfileRepository → 실제 DB 교체

## 문제
- `market_analysis_router.py`에서 `MockUserProfileRepository()`를 사용 중
- account_id 1~3에만 하드코딩된 프로필 반환, 실제 사용자 데이터 미반영
- `UserProfileRepositoryImpl`이 존재하나 메서드명 불일치로 직접 교체 불가

## 구조 문제
- 포트(`market_analysis.UserProfileRepositoryPort`): `get_by_account_id()`
- 구현체(`UserProfileRepositoryImpl`): `find_by_account_id()`
- → 브릿지 메서드 추가 필요

## 부가 문제
- `UserProfileORM`에 `investment_style`, `risk_tolerance`, `preferred_sectors`,
  `analysis_preference` 컬럼 없음
- DB 교체 시 이 필드들은 빈 값 → ContextBuilderService가 빈 컨텍스트 생성
- → `ContextBuilderService.build()`에서 빈 필드 생략 처리 필요

## 구현 범위 (Step 1 — 이번 작업)
1. `UserProfileRepositoryImpl`에 `get_by_account_id()` 브릿지 추가
2. `market_analysis_router.py`: Mock → `UserProfileRepositoryImpl(db)` 교체
3. `ContextBuilderService.build()`: 빈 필드 생략 처리
   - 이후 Step 2(BL-BE-80)에서 ORM 컬럼 추가 시 자동으로 값이 채워짐

## 완료 기준
- 실제 사용자 DB 프로필 기반으로 `preferred_stocks`, `interests_text` 반영
- account_id 1~3 외 사용자도 정상 동작 (프로필 없으면 비개인화 분석)
- 빈 필드로 인한 불필요한 컨텍스트 라인 제거
