from fastapi import APIRouter

from . import routes_health, routes_auth, routes_groups, routes_clients, routes_roles


api_router = APIRouter()

api_router.include_router(routes_health.router, tags=["health"])
api_router.include_router(routes_auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(routes_groups.router, prefix="/groups", tags=["groups"])
api_router.include_router(routes_clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(routes_roles.router, prefix="/roles", tags=["roles"])

