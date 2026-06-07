from fastapi import FastAPI

from server.api import auth
from server.api.admin import users as admin_users
from server.core.exceptions import register_exception_handlers

app = FastAPI(title="PRM Tool API")

register_exception_handlers(app)
app.include_router(auth.router)
app.include_router(admin_users.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
