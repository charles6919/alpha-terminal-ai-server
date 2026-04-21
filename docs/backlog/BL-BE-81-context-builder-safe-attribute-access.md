# BL-BE-81: ContextBuilderService 안전한 속성 접근 처리

## 문제

`context_builder_service.py`의 `build()` 메서드에서 `user_profile` 객체의 필드를
직접 속성 접근(`user_profile.investment_style`)으로 읽는다.

`user_profile` 파라미터 타입이 `Optional[object]`이므로, 예상치 못한 타입의 객체가
전달되거나 향후 리팩토링 과정에서 필드가 누락될 경우 `AttributeError`가 발생하고,
FastAPI가 이를 잡지 못해 AI 응답 전체가 500 오류로 떨어진다.

## 원인

```python
# 직접 접근 — AttributeError 위험
if user_profile.investment_style:
    ...
if user_profile.preferred_sectors:
    ...
```

## 해결 방안

`getattr(obj, attr, default)` 방식으로 안전하게 접근한다.
`UserProfile` 엔티티는 모든 필드에 기본값(`""`, `[]`)이 있으므로,
속성이 없는 경우 동일한 빈 값이 반환되어 조건 분기가 자연스럽게 처리된다.

```python
if getattr(user_profile, 'investment_style', ''):
    ...
```

## 범위

- `app/domains/market_analysis/domain/service/context_builder_service.py`

## 완료 기준

- 7개 필드 모두 `getattr` 방식으로 변경
- 빈 문자열/빈 리스트는 기존과 동일하게 생략
- 기존 동작 변화 없음
