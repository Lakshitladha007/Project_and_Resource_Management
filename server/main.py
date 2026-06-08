from fastapi import FastAPI

from server.api import auth
from server.api.admin import allocations as admin_allocations
from server.api.admin import employees as admin_employees
from server.api.admin import projects as admin_projects
from server.api.admin import users as admin_users
from server.api.employee import timesheets as employee_timesheets
from server.api.manager import allocations as manager_allocations
from server.core.exceptions import register_exception_handlers

app = FastAPI(title="PRM Tool API")

register_exception_handlers(app)
app.include_router(auth.router)
app.include_router(admin_users.router)
app.include_router(admin_employees.router)
app.include_router(admin_projects.router)
app.include_router(admin_allocations.router)
app.include_router(manager_allocations.router)
app.include_router(employee_timesheets.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
