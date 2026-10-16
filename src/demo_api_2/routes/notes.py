"""Notes endpoints: list, read, create, delete."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from demo_api_2.schemas import Note, NoteIn
from demo_api_2.storage import NoteStore

router = APIRouter(prefix="/notes", tags=["notes"])


def get_store(request: Request) -> NoteStore:
    """Return the note store attached to the running app."""
    return request.app.state.note_store


Store = Annotated[NoteStore, Depends(get_store)]


@router.get("")
def list_notes(store: Store) -> list[Note]:
    """List every note."""
    return store.list()


@router.get("/{note_id}")
def get_note(note_id: int, store: Store) -> Note:
    """Return one note, 404 if it does not exist."""
    note = store.get(note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.post("", status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteIn, store: Store) -> Note:
    """Create a note."""
    return store.create(payload)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, store: Store) -> None:
    """Delete one note, 404 if it does not exist."""
    if not store.delete(note_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
