# [INFRA] nginx 502 Bad Gateway — 컨테이너 재배포 후 반복 발생

> 최초 발생: 2026-04-18  
> 심각도: **HIGH** — 서비스 전체 접속 불가  
> 재발 빈도: 매 배포 시마다 발생 가능

---

## 증상

- `https://alpha-desk.duckdns.org` 접속 시 **502 Bad Gateway**
- nginx 로그: 없거나 silent fail
- `alphadesk-web` 컨테이너는 `Up` 상태이나 nginx가 응답을 못 받음

---

## 근본 원인

nginx는 **시작 시점에 upstream 호스트명(`alphadesk-web`)을 DNS 조회하고 IP를 캐시**한다.  
`alphadesk-web`이 재배포되면 컨테이너 IP가 새로 할당된다.  
nginx는 이를 모르고 **죽은 IP로 계속 요청** → 502.

```
nginx 시작 → alphadesk-web IP 캐시 (예: 172.18.0.3)
      ↓
alphadesk-web 재배포 → 새 IP 할당 (예: 172.18.0.5)
      ↓
nginx는 172.18.0.3으로 계속 요청 → Connection refused → 502
```

---

## 즉시 복구 방법

```bash
docker restart alphadesk-nginx
```

nginx를 재시작하면 hostname을 다시 DNS 조회하여 새 IP로 연결된다.

---

## 발생 시점

다음 상황 이후 반드시 확인 필요:

| 상황 | 조치 |
|---|---|
| `alphadesk-web` 재배포 (GitHub Actions 자동 배포) | `docker restart alphadesk-nginx` |
| `alphadesk-web` 수동 재시작 | `docker restart alphadesk-nginx` |
| EC2 인스턴스 재시작 | `docker restart alphadesk-nginx` |
| Docker 네트워크 변경 | `docker restart alphadesk-nginx` |

---

## 근본 해결 (미적용)

nginx.conf에 Docker 내장 DNS resolver를 추가하면 동적으로 IP를 갱신하여 재시작 없이도 동작한다.

```nginx
# /etc/nginx/conf.d/default.conf
resolver 127.0.0.11 valid=30s;

location / {
    set $upstream_web alphadesk-web;
    proxy_pass http://$upstream_web:3000;
}
```

> **주의**: `proxy_pass`에 변수를 쓰면 nginx가 매 요청마다 DNS를 재조회한다.  
> `resolver 127.0.0.11`은 Docker 내장 DNS 서버 주소다.

---

## 관련 이슈

- Docker 네트워크 불일치 문제와 함께 발생하는 경우가 많음
  - `alphadesk-web`과 `alphadesk-nginx`가 같은 네트워크에 있어야 함
  - 현재 기준 네트워크: `alphadesk-network`
- `alphadesk-api` 재배포 후에도 동일 패턴 발생 가능 (nginx가 api를 직접 프록시하는 경우)
