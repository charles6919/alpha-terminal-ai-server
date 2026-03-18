import redis
from app.infrastructure.config.settings import get_settings

_settings = get_settings()

redis_client = redis.Redis(
    host=_settings.redis_host,
    port=_settings.redis_port,
    password=_settings.redis_password or None,
    db=0,
    decode_responses=True,
)
