"""히트맵 upstream 일봉 close 시퀀스 Redis 캐시 (BL-BE-15)."""

from __future__ import annotations

import json
import logging
from typing import List, Optional, Tuple

import redis

logger = logging.getLogger(__name__)

_KEY_PREFIX = "alphadesk:heatmap:closes:v1:"
_DEFAULT_TTL_SEC = 1800


def heatmap_redis_key(cache_key: str) -> str:
    return _KEY_PREFIX + cache_key.replace("|", ":")


def get_closes(
    client: redis.Redis,
    cache_key: str,
) -> Optional[List[Tuple[str, float]]]:
    try:
        raw = client.get(heatmap_redis_key(cache_key))
        if raw is None:
            return None
        data = json.loads(raw)
        if not isinstance(data, list):
            return None
        out: List[Tuple[str, float]] = []
        for pair in data:
            if isinstance(pair, (list, tuple)) and len(pair) == 2:
                out.append((str(pair[0]), float(pair[1])))
        return out or None
    except (redis.RedisError, TypeError, ValueError, json.JSONDecodeError) as e:
        logger.debug("[HeatmapRedis] get failed: %s", type(e).__name__)
        return None


def set_closes(
    client: redis.Redis,
    cache_key: str,
    closes: List[Tuple[str, float]],
    ttl_sec: int = _DEFAULT_TTL_SEC,
) -> None:
    try:
        payload = json.dumps([[d, c] for d, c in closes])
        client.setex(heatmap_redis_key(cache_key), ttl_sec, payload)
    except (redis.RedisError, TypeError, ValueError) as e:
        logger.debug("[HeatmapRedis] set failed: %s", type(e).__name__)
