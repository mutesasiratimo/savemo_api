"""Seed admin role (ACL 'all') and admin user

Revision ID: 0002_seed_admin
Revises: 0001_init_core_models
Create Date: 2026-01-29

"""
import uuid

import bcrypt
from alembic import op
from sqlalchemy import text


revision = "0002_seed_admin_role_and_user"
down_revision = "0001_init_core_models"
branch_labels = None
depends_on = None


ADMIN_EMAIL = "admin@email.com"


def upgrade() -> None:
    hashed = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode("utf-8")
    conn = op.get_bind()

    # Ensure admin role exists
    role_row = conn.execute(text("SELECT id FROM roles WHERE name = 'admin'")).first()
    if role_row is None:
        role_id = uuid.uuid4()
        conn.execute(
            text("""
                INSERT INTO roles (id, name, description, permissions, is_system, created_at, updated_at)
                VALUES (:id, 'admin', 'Platform administrator', '["all"]'::jsonb, true, now(), now())
            """),
            {"id": str(role_id)},
        )
    else:
        role_id = role_row[0]

    # Ensure admin user exists
    user_row = conn.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": ADMIN_EMAIL},
    ).first()
    if user_row is None:
        user_id = uuid.uuid4()
        conn.execute(
            text("""
                INSERT INTO users (id, email, full_name, hashed_password, is_active, is_superuser, created_at, updated_at)
                VALUES (:id, :email, 'Administrator', :pwd, true, false, now(), now())
            """),
            {"id": str(user_id), "email": ADMIN_EMAIL, "pwd": hashed},
        )
    else:
        user_id = user_row[0]

    # Ensure admin user has admin role (platform scope)
    existing = conn.execute(
        text("""
            SELECT 1 FROM user_role_assignments
            WHERE user_id = :user_id AND role_id = :role_id AND scope_type = 'platform'
        """),
        {"user_id": str(user_id), "role_id": str(role_id)},
    ).first()
    if existing is None:
        conn.execute(
            text("""
                INSERT INTO user_role_assignments (id, user_id, role_id, scope_type, created_at)
                VALUES (:id, :user_id, :role_id, 'platform', now())
            """),
            {
                "id": str(uuid.uuid4()),
                "user_id": str(user_id),
                "role_id": str(role_id),
            },
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("DELETE FROM user_role_assignments WHERE scope_type = 'platform' AND role_id IN (SELECT id FROM roles WHERE name = 'admin')"))
    conn.execute(text("DELETE FROM users WHERE email = :email"), {"email": ADMIN_EMAIL})
    conn.execute(text("DELETE FROM roles WHERE name = 'admin'"))
