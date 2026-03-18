from dataclasses import dataclass
from app.domains.auth.domain.value_object.user_role import UserRole


@dataclass
class Session:
    token: str
    user_id: str
    role: UserRole
    ttl_seconds: int
