"""Tests for the /notes endpoints."""

from fastapi.testclient import TestClient


def test_list_is_empty_at_start(client: TestClient) -> None:
    """A fresh app has no notes."""
    response = client.get("/notes")

    assert response.status_code == 200
    assert response.json() == []


def test_create_then_read(client: TestClient) -> None:
    """A created note gets id 1 and can be read back and listed."""
    created = client.post("/notes", json={"text": "hello"})

    assert created.status_code == 201
    assert created.json() == {"id": 1, "text": "hello"}
    assert client.get("/notes/1").json() == {"id": 1, "text": "hello"}
    assert client.get("/notes").json() == [{"id": 1, "text": "hello"}]


def test_get_unknown_note_is_404(client: TestClient) -> None:
    """Reading a missing note answers 404."""
    response = client.get("/notes/42")

    assert response.status_code == 404
    assert response.json() == {"detail": "Note not found"}


def test_create_rejects_empty_text(client: TestClient) -> None:
    """An empty text is a validation error."""
    response = client.post("/notes", json={"text": ""})

    assert response.status_code == 422
