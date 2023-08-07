from fastapi import APIRouter

from sc2sentry.auth.backend import auth_backend
from sc2sentry.auth.fastapi_users_instance import fastapi_users
from sc2sentry.auth.schemas import UserCreate, UserRead, UserUpdate

router_auth = APIRouter(prefix="/auth", tags=["auth"])


# routers
router_auth.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)

router_auth.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

router_auth.include_router(
    fastapi_users.get_reset_password_router(),
)

router_auth.include_router(
    fastapi_users.get_verify_router(UserRead),
)

router_auth.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate, requires_verification=True),
    prefix="/users",
    tags=["users"],
)
