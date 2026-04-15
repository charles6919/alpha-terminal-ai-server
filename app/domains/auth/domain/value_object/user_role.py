from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    NORMAL = "NORMAL"
    USER = "USER"  # 하위 호환 (기존 Redis 세션 대응)
