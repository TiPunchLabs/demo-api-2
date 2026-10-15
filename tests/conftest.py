"""Shared pytest fixtures."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from demo_api_2.main import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Yield a client bound to a fresh app, so every test starts with no notes."""
    with TestClient(create_app()) as test_client:
        yield test_client
