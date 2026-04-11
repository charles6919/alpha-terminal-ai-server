# ISSUE-04: AWS에서 `POST /news/saved` 500 Internal Server Error

작성일: 2026-04-11

---

## 현상

AWS EC2 배포 환경에서 뉴스 목록 화면의 `SAVE` 버튼 클릭 시 저장이 실패했다.

브라우저 콘솔:

```text
POST https://alpha-desk.duckdns.org/api/news/saved 500 (Internal Server Error)
```

프론트 UI에서는 저장 버튼이 `ERROR` 상태로 바뀌었다.

로컬 개발 환경에서는 같은 기능이 정상 동작했기 때문에, 초기에는 EC2 환경 차이 또는 인프라 의존성 문제로 보였다.

---

## 1차 가설

뉴스 저장 기능은 두 저장소를 함께 사용한다.

- MySQL: `saved_articles` 메타데이터
- PostgreSQL(JSONB): `saved_article_contents` 기사 본문 원본

따라서 처음에는 AWS에서 PostgreSQL 컨테이너가 없거나, API 컨테이너의 `PG_HOST`가 잘못되어 후처리 저장 단계에서 500이 나는 것으로 의심했다.

실제 확인한 내용:

- `pg-container` 컨테이너가 EC2에서 실행 중
- `alphadesk-api`, `pg-container` 모두 `alphadesk-network`에 연결됨
- API 컨테이너 env:

```text
PG_HOST=pg-container
PG_PORT=5432
PG_USER=eddi
PG_DATABASE=appdb
```

- API 컨테이너 내부 DNS 확인:

```bash
docker exec alphadesk-api getent hosts pg-container
# 172.18.0.7      pg-container
```

즉, PostgreSQL 네트워크/환경변수 자체는 문제가 아니었다.

---

## 실제 원인

백엔드 로그를 확인한 결과, 실제 예외는 PostgreSQL이 아니라 **MySQL 스키마 불일치**였다.

에러 핵심:

```text
sqlalchemy.exc.OperationalError:
(pymysql.err.OperationalError) (1054, "Unknown column 'saved_articles.account_id' in 'field list'")
```

문제 쿼리:

```sql
SELECT ...
FROM saved_articles
WHERE saved_articles.link_hash = ? AND saved_articles.account_id = ?
```

현재 코드/ORM은 `saved_articles.account_id`를 기준으로

- 사용자별 중복 저장 검사
- `(account_id, link_hash)` 유니크 제약

를 사용한다. 하지만 EC2 MySQL 볼륨에 남아 있던 운영 테이블은 **이전 스키마**라서 `account_id` 컬럼이 없었다.

정리:

- 코드: 최신 스키마 기준
- 운영 MySQL: 구 스키마 기준
- 결과: 저장 전 중복 검사 쿼리에서 즉시 500 발생

---

## 확인 과정

### 1. 백엔드 로그 확인

```bash
docker logs -f alphadesk-api
```

이 로그에서 `Unknown column 'saved_articles.account_id'`를 확인했다.

### 2. MySQL 컨테이너 및 접속 정보 확보

```bash
MYSQL_C=$(docker ps --filter ancestor=mysql:8.0 --format '{{.Names}}' | head -1)
MYSQL_USER=$(docker exec alphadesk-api printenv MYSQL_USER)
MYSQL_PASSWORD=$(docker exec alphadesk-api printenv MYSQL_PASSWORD)
MYSQL_DATABASE=$(docker exec alphadesk-api printenv MYSQL_DATABASE)
```

실제 값:

```text
MYSQL_C=alphadesk-mysql
MYSQL_USER=eddi
MYSQL_DATABASE=multi_agent_db
```

### 3. 운영 테이블 구조 확인

```bash
docker exec -it "$MYSQL_C" mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -e "
SHOW CREATE TABLE saved_articles\G
SHOW INDEX FROM saved_articles;
"
```

여기서 `account_id`가 없음을 확인했다.

---

## 해결

운영 MySQL에 직접 스키마 패치를 적용했다.

### 1. `account_id` 컬럼 추가

```bash
docker exec -it "$MYSQL_C" mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -e "
ALTER TABLE saved_articles
  ADD COLUMN account_id INT NOT NULL DEFAULT 0;
"
```

### 2. 구 `content` 컬럼 제거

```bash
docker exec -it "$MYSQL_C" mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -e "
ALTER TABLE saved_articles DROP COLUMN content;
"
```

`content` 컬럼이 이미 없으면 이 단계는 생략 가능하다.

### 3. 인덱스 정리

과거 스키마에서는 `link_hash` 단독 인덱스가 있었을 수 있으므로 제거를 시도했다.

```bash
docker exec -it "$MYSQL_C" mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -e "
ALTER TABLE saved_articles DROP INDEX link_hash;
"
```

실제 운영 DB에서는 아래 에러가 나왔다:

```text
ERROR 1091 (42000): Can't DROP 'link_hash'; check that column/key exists
```

즉, 해당 이름의 인덱스는 이미 없었고 다음 단계로 진행했다.

### 4. 최신 유니크 인덱스 추가

```bash
docker exec -it "$MYSQL_C" mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -e "
ALTER TABLE saved_articles
  ADD UNIQUE INDEX uq_saved_articles_account_link (account_id, link_hash);
"
```

### 5. 최종 확인

```bash
docker exec -it "$MYSQL_C" mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -e "
SHOW CREATE TABLE saved_articles\G
SHOW INDEX FROM saved_articles;
"
```

정상 상태:

```sql
CREATE TABLE `saved_articles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(500) NOT NULL,
  `link` text NOT NULL,
  `link_hash` varchar(64) NOT NULL,
  `source` varchar(255) NOT NULL,
  `snippet` text DEFAULT NULL,
  `published_at` varchar(100) DEFAULT NULL,
  `saved_at` datetime DEFAULT NULL,
  `account_id` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_saved_articles_account_link` (`account_id`,`link_hash`)
)
```

이후 브라우저에서 `SAVE` 재시도 시 정상 저장되는 것을 확인했다.

---

## 왜 로컬에서는 괜찮았나

로컬은 새 컨테이너/새 볼륨 기준으로 개발해 최신 ORM 구조가 자연스럽게 맞춰져 있었다.

반면 AWS EC2는 기존 MySQL 데이터 볼륨을 계속 재사용하고 있었고, `saved_articles`가 과거 구조를 유지한 채 남아 있었다. 즉, 문제는 코드가 아니라 **운영 DB 스키마 드리프트**였다.

---

## 재발 방지

### 1. 배포 후 스키마 체크 추가

뉴스 저장 관련 변경을 배포한 뒤 최소 아래를 확인한다.

```bash
docker exec -it "$MYSQL_C" mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -e "
SHOW CREATE TABLE saved_articles\G
SHOW INDEX FROM saved_articles;
"
```

확인 포인트:

- `account_id` 컬럼 존재
- `uq_saved_articles_account_link (account_id, link_hash)` 존재

### 2. 앱 시작 시 migration 실패를 로그로 남기기

`main.py`의 `_run_column_migrations()`는 예외를 삼켜 계속 기동할 수 있도록 되어 있다. 이 방식은 서비스 가용성에는 유리하지만, 운영에서는 실제 스키마 보정이 누락되어도 문제를 늦게 발견할 수 있다.

향후 개선 후보:

- migration 결과를 명시적으로 로그 출력
- startup check에서 필수 컬럼 누락 시 경고 또는 실패 처리
- Alembic 등 명시적 마이그레이션 도입

### 3. PostgreSQL 이슈와 분리해서 본다

`/news/saved`는 PostgreSQL도 사용하지만, 이번 장애의 직접 원인은 MySQL이었다. 운영 디버깅 시에는 다음 순서로 보는 것이 효율적이다.

1. API 로그에서 실제 traceback 확인
2. MySQL 스키마/쿼리 오류 확인
3. 그 다음 PostgreSQL 연결/JSONB 저장 경로 확인

---

## 결론

이번 장애는 **AWS에서 PostgreSQL 미기동 문제**가 아니라, **운영 MySQL의 `saved_articles` 테이블이 최신 코드가 기대하는 스키마(`account_id` 포함)로 올라오지 않은 것**이 원인이었다.

EC2에서 `saved_articles`에 `account_id` 컬럼을 추가하고, `(account_id, link_hash)` 유니크 인덱스를 맞춘 뒤 정상화되었다.
