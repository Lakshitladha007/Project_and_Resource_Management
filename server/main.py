from fastapi import FastAPI

from server.api import auth
from server.core.exceptions import register_exception_handlers

app = FastAPI(title="PRM Tool API")

register_exception_handlers(app)
app.include_router(auth.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
