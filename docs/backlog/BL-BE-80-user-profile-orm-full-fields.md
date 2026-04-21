# BL-BE-80: UserProfileORM 전체 필드 추가 + My Page 입력 연동

## 문제
- `UserProfileORM`에 `preferred_stocks`, `interests_text`만 저장됨
- `investment_style`, `risk_tolerance`, `preferred_sectors`, `analysis_preference`,
  `keywords_of_interest`는 DB 컬럼 없어서 항상 빈 값
- BL-BE-79 교체 후에도 AI 개인화 컨텍스트의 핵심 필드가 비어있는 상태

## 구현 범위
1. `UserProfileORM` 컬럼 추가:
   - `investment_style` VARCHAR(20) DEFAULT ""
   - `risk_tolerance` VARCHAR(20) DEFAULT ""
   - `preferred_sectors` TEXT DEFAULT "" (JSON)
   - `analysis_preference` VARCHAR(20) DEFAULT ""
   - `keywords_of_interest` TEXT DEFAULT "" (JSON)
2. Alembic MySQL migration 추가
3. `UserProfileMapper.to_entity()` / `to_orm()` 업데이트
4. `UserProfileRepositoryImpl.save()` 업데이트
5. FE My Page에서 이 필드들 입력 받는 UI/API 추가 (BL-FE-76 연동)

## 선행 조건
- BL-BE-79 완료 후 진행
- 운영 DB 백업 필수

## 완료 기준
- My Page에서 투자 스타일/위험 허용도/관심 섹터 설정 가능
- AI 분석 시 사용자가 설정한 프로필 컨텍스트로 개인화 응답
