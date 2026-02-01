"""
ACLs (permissions) are defined in code and attached to roles.
The special permission "all" grants every permission.
"""

from typing import Set

# All permission codes used in the system (embedded in code).
# "all" is special: it grants every permission.
PERMISSION_ALL = "all"

PERMISSIONS: Set[str] = {
    PERMISSION_ALL,
    # System
    "system.admin",
    # Groups
    "group.manage_members",
    "group.manage_goals",
    "group.approve_loans",
    "group.view",
    # Wallet / finance
    "wallet.view",
    "wallet.debit",
    "wallet.credit",
    "finance.manage_invoices",
    # Events & notifications
    "events.manage",
    "notifications.configure",
}


def has_permission(user_permissions: Set[str], required: str) -> bool:
    """Return True if user has the required permission."""
    if PERMISSION_ALL in user_permissions:
        return True
    return required in user_permissions


def has_any_permission(user_permissions: Set[str], required: Set[str]) -> bool:
    """Return True if user has at least one of the required permissions."""
    if PERMISSION_ALL in user_permissions:
        return True
    return bool(required & user_permissions)


def has_all_permissions(user_permissions: Set[str], required: Set[str]) -> bool:
    """Return True if user has every required permission."""
    if PERMISSION_ALL in user_permissions:
        return True
    return required <= user_permissions
