from typing import Set

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.routes_auth import get_current_user
from app.core.acl import has_any_permission
from app.core.permissions import get_user_permissions
from app.db.session import get_db
from app.models.user import User


def get_current_user_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Set[str]:
    return get_user_permissions(db, current_user.id)


def require_permissions(*required: str):
    """Dependency that requires the current user to have at least one of the given permissions."""

    def _require(
        perms: Set[str] = Depends(get_current_user_permissions),
    ) -> Set[str]:
        required_set = set(required)
        if not required_set:
            return perms
        if not has_any_permission(perms, required_set):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return perms

    return _require


def require_permission(required: str):
    """Dependency that requires the current user to have the given permission."""
    return require_permissions(required)
