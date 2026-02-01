from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    phone: str | None = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


class UserMeRead(UserBase):
    """Current user profile with effective ACLs (replaces is_superuser)."""

    id: UUID
    is_active: bool
    permissions: list[str]

    class Config:
        from_attributes = True

