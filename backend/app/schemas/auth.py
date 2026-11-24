from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

def normalize_email(email):
    """メールアドレスを正規化する。大文字を小文字に変換し、前後の空白を削除する。"""
    if isinstance(email, str):
        return email.strip().lower()
    return email

class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def _normalize_email(cls, v: object):
        return normalize_email(v)

class LoginRequest(BaseModel):
    email: EmailStr = Field(max_length=254)
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def _normalize_email(cls, v: object):
        return normalize_email(v)

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime|None = None
    model_config = ConfigDict(from_attributes=True)