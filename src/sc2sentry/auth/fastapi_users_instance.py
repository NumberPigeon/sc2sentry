import uuid

from fastapi_users import FastAPIUsers

from sc2sentry.auth.backend import auth_backend
from sc2sentry.auth.manager import get_user_manager
from sc2sentry.auth.models import User

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)
