"""Load user permissions from DB (no dependency on API layer)."""

import uuid
from datetime import datetime, timezone
from typing import Set

from sqlalchemy.orm import Session, joinedload

from app.models.role import UserRoleAssignment


def get_user_permissions(db: Session, user_id: uuid.UUID) -> Set[str]:
    """Load effective permissions for a user from their platform-level role assignments."""
    now = datetime.now(timezone.utc)
    assignments = (
        db.query(UserRoleAssignment)
        .filter(
            UserRoleAssignment.user_id == user_id,
            UserRoleAssignment.scope_type == "platform",
        )
        .options(joinedload(UserRoleAssignment.role))
        .all()
    )
    perms: Set[str] = set()
    for a in assignments:
        if a.starts_at and a.starts_at > now:
            continue
        if a.ends_at and a.ends_at < now:
            continue
        if a.role and a.role.permissions:
            perms.update(a.role.permissions)
    return perms
