from fastapi import FastAPI

from server.api import auth
from server.api.admin import employees as admin_employees
from server.api.admin import projects as admin_projects
from server.api.admin import users as admin_users
from server.core.exceptions import register_exception_handlers

app = FastAPI(title="PRM Tool API")

register_exception_handlers(app)
app.include_router(auth.router)
app.include_router(admin_users.router)
app.include_router(admin_employees.router)
app.include_router(admin_projects.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
