"""FastAPI application factory."""

from fastapi import FastAPI

from demo_api_2 import __version__
from demo_api_2.routes import health, notes
from demo_api_2.storage import NoteStore


def create_app() -> FastAPI:
    """Build the application with a fresh in-memory note store."""
    app = FastAPI(title="demo-api-2", version=__version__)
    app.state.note_store = NoteStore()
    app.include_router(health.router)
    app.include_router(notes.router)
    return app


app = create_app()
