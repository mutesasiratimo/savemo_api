from uuid import UUID

from pydantic import BaseModel


class GroupBase(BaseModel):
    name: str
    code: str | None = None
    description: str | None = None
    parent_group_id: UUID | None = None


class GroupCreate(GroupBase):
    pass


class GroupRead(GroupBase):
    id: UUID
    status: str

    class Config:
        from_attributes = True

