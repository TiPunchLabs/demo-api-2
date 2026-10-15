"""demo-api-2: minimal FastAPI notes service used as the second FlowForge target."""

from importlib.metadata import version

__version__ = version("demo-api-2")


def main() -> None:
    """Run the development server (entry point of the `demo-api-2` script)."""
    import uvicorn

    uvicorn.run("demo_api_2.main:app", host="127.0.0.1", port=8000)
