from fastapi import FastAPI

from sc2sentry.auth.routers import router_auth

app = FastAPI()

app.include_router(router_auth)
