import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.modules.users.schemas import UserOut


def _check_password_strength(value: str) -> str:
    if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
        raise ValueError("Password must contain at least one letter and one digit.")
    return value


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("full_name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name must not be blank.")
        return v

    _pw = field_validator("password")(_check_password_strength)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    """Only used by native clients (Tauri, mobile, CLI). Browsers use the HttpOnly cookie."""

    refresh_token: str | None = Field(default=None, max_length=200)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    new_password: str = Field(min_length=12, max_length=128)

    _pw = field_validator("new_password")(_check_password_strength)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token lifetime in seconds.")
    refresh_token: str | None = Field(
        default=None, description="Returned only to native clients (X-ArtifactX-Client: native)."
    )
    user: UserOut
