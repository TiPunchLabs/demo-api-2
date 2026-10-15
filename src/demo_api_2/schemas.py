"""Pydantic models of the notes API."""

from pydantic import BaseModel, Field


class NoteIn(BaseModel):
    """Payload to create a note."""

    text: str = Field(min_length=1, max_length=500)


class Note(NoteIn):
    """A stored note."""

    id: int
