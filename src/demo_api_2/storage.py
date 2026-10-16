"""In-memory note repository."""

from demo_api_2.schemas import Note, NoteIn


class NoteStore:
    """Notes kept in a dict, keyed by an incrementing id."""

    def __init__(self) -> None:
        """Start empty; ids start at 1."""
        self._notes: dict[int, Note] = {}
        self._next_id = 1

    def list(self) -> list[Note]:
        """Return every note, by ascending id."""
        return [self._notes[key] for key in sorted(self._notes)]

    def get(self, note_id: int) -> Note | None:
        """Return the note with this id, or None."""
        return self._notes.get(note_id)

    def delete(self, note_id: int) -> bool:
        """Remove the note with this id; return whether it existed."""
        return self._notes.pop(note_id, None) is not None

    def create(self, payload: NoteIn) -> Note:
        """Store a new note and return it with its id."""
        note = Note(id=self._next_id, **payload.model_dump())
        self._notes[note.id] = note
        self._next_id += 1
        return note
