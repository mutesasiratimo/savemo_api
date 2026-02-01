from uuid import UUID

from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str
    description: str | None = None
    permissions: list[str] = []


class RoleCreate(RoleBase):
    is_system: bool = False


class RoleRead(RoleBase):
    id: UUID
    is_system: bool

    class Config:
        from_attributes = True
