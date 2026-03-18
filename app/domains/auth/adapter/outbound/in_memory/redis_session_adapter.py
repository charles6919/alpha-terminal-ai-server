import json
from typing import Optional

import redis

from app.domains.auth.application.usecase.session_store_port import SessionStorePort
from app.domains.auth.domain.entity.session import Session
from app.domains.auth.domain.value_object.user_role import UserRole

SESSION_KEY_PREFIX = "session:"


class RedisSessionAdapter(SessionStorePort):

    def __init__(self, redis_client: redis.Redis):
        self._redis = redis_client

    def save(self, session: Session) -> None:
        key = SESSION_KEY_PREFIX + session.token
        data = {
            "token": session.token,
            "user_id": session.user_id,
            "role": session.role.value,
        }
        self._redis.setex(key, session.ttl_seconds, json.dumps(data))

    def find_by_token(self, token: str) -> Optional[Session]:
        key = SESSION_KEY_PREFIX + token
        raw = self._redis.get(key)
        if raw is None:
            return None
        data = json.loads(raw)
        ttl = self._redis.ttl(key)
        return Session(
            token=data["token"],
            user_id=data["user_id"],
            role=UserRole(data["role"]),
            ttl_seconds=ttl,
        )

    def delete(self, token: str) -> None:
        key = SESSION_KEY_PREFIX + token
        self._redis.delete(key)
