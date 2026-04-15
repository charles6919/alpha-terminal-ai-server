from typing import Optional

from pydantic import BaseModel


class RegisterAccountRequest(BaseModel):
    nickname: str
    email: str
    admin_code: Optional[str] = None
