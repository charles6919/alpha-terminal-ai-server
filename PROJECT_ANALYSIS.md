# Project Analysis: alpha-desk-ai-server

> 분석 일자: 2026-03-14

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **프로젝트명** | alpha-desk-ai-server (alphadesk-backend) |
| **프레임워크** | FastAPI (Python) |
| **아키텍처** | Hexagonal Architecture + Domain Driven Design (DDD) |
| **서버 포트** | 33333 |
| **현재 상태** | 초기 뼈대(Skeleton) 단계 |

---

## 2. 현재 디렉토리 구조

```
alpha-desk-ai-server/
├── app/
│   ├── __init__.py
│   └── infrastructure/
│       ├── __init__.py
│       └── config/
│           ├── __init__.py
│           └── settings.py          ✅ 구현됨
├── main.py                          ✅ 구현됨
├── requirements.txt
├── test_main.http
├── README.md
└── CLAUDE.md                        (아키텍처 가이드)
```

### 목표 구조 (CLAUDE.md 기준)

```
app/
├── domains/
│   └── <domain_name>/
│       ├── domain/
│       │   ├── entity/              ❌ 미구현
│       │   ├── value_object/        ❌ 미구현
│       │   └── service/             ❌ 미구현
│       ├── application/
│       │   ├── usecase/             ❌ 미구현
│       │   ├── request/             ❌ 미구현
│       │   └── response/            ❌ 미구현
│       ├── adapter/
│       │   ├── inbound/api/         ❌ 미구현
│       │   └── outbound/
│       │       ├── persistence/     ❌ 미구현
│       │       └── external/        ❌ 미구현
│       └── infrastructure/
│           ├── orm/                 ❌ 미구현
│           └── mapper/              ❌ 미구현
└── infrastructure/
    ├── config/                      ✅ 구현됨
    ├── database/                    ❌ 미구현
    ├── cache/                       ❌ 미구현
    └── external/                    ❌ 미구현
```

---

## 3. 구현된 파일 분석

### main.py

```python
from fastapi import FastAPI
from app.infrastructure.config.settings import Settings, get_settings

settings: Settings = get_settings()
app = FastAPI(debug=settings.debug)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

- FastAPI 앱 초기화
- Settings 싱글톤 주입
- `/` 엔드포인트 1개만 존재
- 포트 33333으로 실행

### infrastructure/config/settings.py

```python
class Settings(BaseSettings):
    mysql_user: str
    mysql_password: str
    mysql_host: str
    mysql_port: int
    mysql_database: str
    debug: bool = False
```

- `pydantic-settings` 기반 환경변수 관리
- `.env` 파일 로드 지원
- `@lru_cache`로 싱글톤 패턴 적용
- MySQL 접속 정보 정의됨 (실제 연결은 미구현)

---

## 4. 의존성 (requirements.txt)

| 패키지 | 버전 | 용도 |
|--------|------|------|
| fastapi | >=0.115.0 | 웹 프레임워크 |
| uvicorn | >=0.34.0 | ASGI 서버 |
| pydantic-settings | >=2.7.0 | 환경설정 관리 |

### 미설치 (추후 필요)

| 패키지 | 용도 |
|--------|------|
| SQLAlchemy | ORM |
| pymysql / aiomysql | MySQL 드라이버 |
| redis | Redis 클라이언트 |
| alembic | DB 마이그레이션 |

---

## 5. 알려진 이슈

| # | 이슈 | 위치 | 심각도 |
|---|------|------|--------|
| 1 | `test_main.http`가 포트 8000을 참조하나 서버는 33333 | test_main.http | Low |
| 2 | `test_main.http`의 `/hello/User` 엔드포인트 미구현 | test_main.http | Low |
| 3 | MySQL Settings는 정의되었으나 실제 DB 연결 없음 | settings.py | Medium |
| 4 | `.env` 파일 없으면 서버 시작 실패 | settings.py | High |

---

## 6. 아키텍처 규칙 준수 현황

| 규칙 | 상태 | 비고 |
|------|------|------|
| Domain Layer = 순수 Python | ✅ N/A | 아직 미구현 |
| ORM ≠ Domain Entity | ✅ N/A | 아직 미구현 |
| Request/Response DTO 분리 | ✅ N/A | 아직 미구현 |
| Router에 비즈니스 로직 금지 | ✅ 준수 | main.py는 단순 헬스체크만 |
| Infrastructure Config 위치 | ✅ 준수 | `app/infrastructure/config/` |

---

## 7. 스킬(Skills) 분석

Claude Code에 등록된 활성 스킬 목록:

### keybindings-help
- **목적**: 키보드 단축키 커스터마이징
- **트리거**: 키바인딩 변경, 코드 제출 키 변경 요청
- **파일**: `~/.claude/keybindings.json`

### claude-developer-platform
- **목적**: Anthropic SDK / Claude API를 사용하는 앱 빌드
- **트리거**: `anthropic` SDK import, Claude API 연동 요청
- **주의**: OpenAI, Gemini 등 타 SDK 사용 시 트리거 안 됨

### 삭제된 스킬 (git 기록 기준)
이전에 존재했으나 현재 삭제된 파일:

| 파일 | 설명 |
|------|------|
| `.claude/commands/backlog.md` | 백로그 관련 커스텀 커맨드 |
| `.claude/commands/implement.md` | 구현 관련 커스텀 커맨드 |
| `.claude/skills/BEHAVIOR_BACKLOG_GENERATOR.md` | 백로그 생성 스킬 |
| `.claude/settings.local.json` | 로컬 Claude 설정 |

---

## 8. Git 이력

| 커밋 | 메시지 |
|------|--------|
| `c0f14ff` | Update README title to alphadesk-backend |
| `586da8f` | Add .claude directory |
| `fd1f4fc` | Initial project setup with FastAPI base structure |

---

## 9. 다음 단계 권장사항

### 즉시 필요
1. `.env` 파일 생성 (MySQL 접속 정보 입력)
2. `test_main.http` 포트 8000 → 33333 수정

### 단기 (첫 번째 도메인 구현)
1. 첫 번째 도메인 결정 및 `domains/<name>/` 구조 생성
2. SQLAlchemy 설치 및 `infrastructure/database/` 구현
3. Domain Entity, Repository Port 정의
4. UseCase 구현
5. FastAPI Router 추가 (`adapter/inbound/api/`)

### 중기
1. Redis 캐시 레이어 구현
2. 인증/인가 미들웨어 추가
3. 에러 핸들링 표준화
4. 단위 테스트 작성

---

## 10. 결론

이 프로젝트는 **Hexagonal Architecture + DDD** 원칙을 따르는 FastAPI 백엔드의 **초기 설정 단계**이다. 인프라 구성(`settings.py`)은 올바르게 구현되었고, CLAUDE.md에 명확한 아키텍처 가이드라인이 정의되어 있다. 현재는 비즈니스 도메인 구현 전 단계로, 첫 번째 도메인의 설계와 구현이 다음 핵심 작업이다.
