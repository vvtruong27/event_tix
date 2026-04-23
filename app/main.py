"""Application entrypoint for the EventTix API service.

This module creates the FastAPI application instance, wires route modules,
and exposes a small health-style root endpoint for quick verification.
"""

from fastapi import FastAPI
from app.api import events, users

# Create one global application object used by ASGI servers (uvicorn/gunicorn).
app = FastAPI(title="EventTix API", description="High-Concurrency Ticketing Platform")

# Register feature routers. Each router owns its own URL prefix and tags.
app.include_router(users.router)
app.include_router(events.router)

@app.get("/")
async def root():
    """Return a simple message confirming the API is reachable."""
    return {"message": "Welcome to EventTix! The infrastructure is ready."}