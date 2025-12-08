from .routers.auth_router import auth_router
from .routers.permission_router import permission_router
from .routers.role_router import role_router

__all__ = ["auth_router", "role_router", "permission_router"]
