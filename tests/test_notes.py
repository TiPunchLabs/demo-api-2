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


def test_delete_note(client: TestClient) -> None:
    """Deleting a note answers 204 and removes it everywhere."""
    client.post("/notes", json={"text": "hello"})

    response = client.delete("/notes/1")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/notes").json() == []
    assert client.get("/notes/1").status_code == 404


def test_delete_unknown_note_is_404(client: TestClient) -> None:
    """Deleting a missing note answers 404."""
    response = client.delete("/notes/42")

    assert response.status_code == 404
    assert response.json() == {"detail": "Note not found"}


def test_delete_rejects_non_integer_id(client: TestClient) -> None:
    """A non-integer id is a validation error."""
    assert client.delete("/notes/abc").status_code == 422


def test_deleted_id_is_not_reused(client: TestClient) -> None:
    """A note created after a delete gets a fresh id."""
    client.post("/notes", json={"text": "first"})
    client.delete("/notes/1")

    created = client.post("/notes", json={"text": "second"})

    assert created.json() == {"id": 2, "text": "second"}
