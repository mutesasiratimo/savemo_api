from uuid import UUID

from pydantic import BaseModel


class ClientBase(BaseModel):
    name: str
    tagline: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None


class ClientCreate(ClientBase):
    # logo will be uploaded separately or as base64 in a later iteration
    pass


class ClientRead(ClientBase):
    id: UUID
    default_group_id: UUID

    class Config:
        from_attributes = True

