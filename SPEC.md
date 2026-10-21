# demo-api-2 — Specification

> **Role**: functional source of truth of `demo-api-2`. `README.md` remains the user-facing
> documentation (endpoint table, usage).
> **Status**: owner decisions of 2026-10-19 applied; aligned with the FlowForge `SPEC.md` contract on
> 2026-10-21 (section title, undecided status code, coverage); under human review (PR).
>
> Reliability tags:
> - `CONFIRMED` — contractual requirement (README, CLAUDE.md, owner-approved Issue or owner decision).
> - `OBSERVED` — current implementation detail, **not** contractual. Agents may rely on it today
>   but must not treat it as a constraint, nor promote it to a requirement without owner approval.
> - `KNOWN GAP` — confirmed requirement that the current implementation does not meet yet
>   (tracked in `docs/flowforge-spec-review.md`, technical debt section).
>
> Evidence, decisions log and open questions: `docs/flowforge-spec-review.md`.

------

## 1. Objective and scope

**Purpose.** `demo-api-2` is a minimal HTTP service to create, list, read and delete short
text notes, plus a liveness check. Its main role is to be a small, fully tested **target
repository for FlowForge**: AI agents receive GitHub Issues and open Draft PRs against it.

**Consumers.** HTTP clients of the JSON API, and the FlowForge agents that evolve it.

**Responsibilities.**
- Expose a liveness endpoint.
- Manage a collection of notes: create, list, read one, delete one.
- Validate note input and report errors with standard HTTP status codes.

**Functional limits (current scope).**
- Storage is in memory: notes are lost on restart and not shared between processes. `CONFIRMED`
- No update/edit of a note: intentional for the current scope; a future Issue may add it. `CONFIRMED`
- No search, filtering or pagination. `OBSERVED`
- No authentication, authorization or user ownership of notes. `OBSERVED`
- A note holds only an `id` and a `text`; no timestamps, title or other metadata. `CONFIRMED`

Any request that crosses one of these limits is a scope extension and must be explicit in its Issue.

------

## 2. Features

### F-001 — Liveness check

**Description:** The service reports that it is up, with no dependency on stored data.

**Related rules:** —

### F-002 — Create a note

**Description:** A client submits a text; the service validates it, stores it as a new note,
assigns its id and returns the created note.

**Related rules:** R-001, R-002, R-003, R-004, R-009

### F-003 — List notes

**Description:** A client retrieves every stored note in a single response.

**Related rules:** R-001, R-005, R-008

### F-004 — Read a note

**Description:** A client retrieves one note by its id.

**Related rules:** R-001, R-006, R-007

### F-005 — Delete a note

**Description:** A client deletes one note by its id; the note then disappears from every
read operation.

**Related rules:** R-003, R-006, R-007

------

## 3. Rules and constraints

### R-001 — Note representation

**Requirement:** A note is exposed as a JSON object `{"id": int, "text": str}`, and every
endpoint returning notes uses this shape. `CONFIRMED`

### R-002 — Text validation

**Requirement:** A note text is a string of 1 to 500 characters (inclusive) that contains at
least one non-whitespace character. `CONFIRMED`

- A creation request whose `text` is missing, not a string, empty or longer than 500 characters
  is rejected with `422` and nothing is stored. `CONFIRMED`
- A creation request whose `text` is whitespace-only (e.g. `"   "`) is rejected and nothing is
  stored. `CONFIRMED`

> The status code of the whitespace-only rejection is **not decided** (Q-07 in
> `docs/flowforge-spec-review.md`): `422` is the proposed value, by consistency with the other
> text errors, and is not contractual until the owner confirms it.
>
> `KNOWN GAP` — whitespace-only texts are currently accepted (`201`). See TD-01.

### R-003 — Ids are unique and never reused

**Requirement:** The service assigns every note an id that is unique among all ids it has
issued. An id is never issued again during the life of the service, even after its note is
deleted. `CONFIRMED`

### R-004 — Clients do not control ids

**Requirement:** Ids are assigned by the service only. Data sent by a client in a creation
request must never determine the id of the created note, nor overwrite or alter an existing
note. `CONFIRMED`

> How a client-supplied `id` field is handled (ignored or rejected) is **not** contractual.
>
> `OBSERVED` implementation details, not contractual: ids start at `1` and increase by one per
> created note; unknown fields in the creation payload (including `id`) are silently ignored.

### R-005 — List order

**Requirement:** The list of notes is returned sorted by ascending id. An empty store
returns an empty list (`200 []`). `CONFIRMED`

### R-006 — Unknown note

**Requirement:** Reading or deleting an id that does not exist (never issued or already
deleted) answers `404` with the body `{"detail": "Note not found"}` and changes nothing.
`CONFIRMED`

### R-007 — Malformed id

**Requirement:** A path id that is not an integer answers `422` on read and delete. `CONFIRMED`

### R-008 — In-memory, per-instance storage

**Requirement:** Notes live only in memory, in the running service instance. A fresh
instance starts with no notes; data is not persisted and not shared across workers.
Introducing persistence requires an Issue that explicitly asks for it. `CONFIRMED`

### R-009 — Id uniqueness under concurrency

**Requirement:** Concurrent creation requests on the same service instance never produce two
notes with the same id. `CONFIRMED`

> `KNOWN GAP` — not guaranteed by the implementation (no synchronisation around id
> assignment). See TD-02.

------

## 4. Validation scenarios

`Coverage` is `COVERED` (every THEN is asserted by the cited test), `PARTIAL` (some THEN only)
or `NOT_COVERED` (no test).
Scenarios marked `KNOWN GAP` describe required behaviour that the code does not meet yet.

### S-001 — Service is up

**Covers:** F-001 — Coverage: `COVERED` (`test_health_returns_ok`)

GIVEN a running service
WHEN the client sends `GET /health`
THEN the response is `200` with body `{"status": "ok"}`

### S-002 — Fresh instance has no notes

**Covers:** F-003, R-005, R-008 — Coverage: `COVERED` (`test_list_is_empty_at_start`)

GIVEN a freshly started service
WHEN the client sends `GET /notes`
THEN the response is `200` with body `[]`

### S-003 — Create then read back

**Covers:** F-002, F-003, F-004, R-001 — Coverage: `COVERED` (`test_create_then_read`)

GIVEN a freshly started service
WHEN the client sends `POST /notes` with `{"text": "hello"}`
THEN the response is `201` with a note `{"id": <N>, "text": "hello"}` where `<N>` is an integer
AND `GET /notes/<N>` returns that note
AND `GET /notes` returns exactly `[that note]`

### S-004 — Invalid text is rejected

**Covers:** F-002, R-002 — Coverage: `PARTIAL` (`test_create_rejects_empty_text`: empty text only;
missing, non-string and 501-character `text`, and the "no new note" check, are not asserted)

GIVEN a running service
WHEN the client sends `POST /notes` with `{"text": ""}`, with `{}`, with a non-string `text`,
or with a 501-character `text`
THEN each response is `422`
AND `GET /notes` contains no new note

### S-005 — Whitespace-only text is rejected

**Covers:** F-002, R-002 — Coverage: `NOT_COVERED` — `KNOWN GAP` (TD-01)

GIVEN a running service
WHEN the client sends `POST /notes` with `{"text": "   "}`
THEN the request is rejected (status code not decided, Q-07)
AND `GET /notes` contains no new note

### S-006 — Maximum length is accepted

**Covers:** F-002, R-002 — Coverage: `NOT_COVERED`

GIVEN a running service
WHEN the client sends `POST /notes` with a `text` of exactly 500 characters
THEN the response is `201` and the note holds the full text

### S-007 — List is ordered by id

**Covers:** F-003, R-005 — Coverage: `NOT_COVERED`

GIVEN notes created with texts `"a"`, `"b"`, `"c"`
WHEN the client sends `GET /notes`
THEN the notes are returned by strictly ascending id

### S-008 — Read an unknown note

**Covers:** F-004, R-006 — Coverage: `COVERED` (`test_get_unknown_note_is_404`)

GIVEN no note with id `42`
WHEN the client sends `GET /notes/42`
THEN the response is `404` with body `{"detail": "Note not found"}`

### S-009 — Delete a note

**Covers:** F-005 — Coverage: `COVERED` (`test_delete_note`)

GIVEN an existing note with id `<N>`
WHEN the client sends `DELETE /notes/<N>`
THEN the response is `204` with an empty body
AND `GET /notes` no longer contains it
AND `GET /notes/<N>` answers `404`

### S-010 — Delete an unknown note

**Covers:** F-005, R-006 — Coverage: `COVERED` (`test_delete_unknown_note_is_404`)

GIVEN no note with id `42`
WHEN the client sends `DELETE /notes/42`
THEN the response is `404` with body `{"detail": "Note not found"}`

### S-011 — Malformed id

**Covers:** F-004, F-005, R-007 — Coverage: `PARTIAL` (`test_delete_rejects_non_integer_id`: delete only)

GIVEN a running service
WHEN the client sends `GET /notes/abc` or `DELETE /notes/abc`
THEN each response is `422`

### S-012 — Deleted ids are not reused

**Covers:** F-002, F-005, R-003 — Coverage: `COVERED` (`test_deleted_id_is_not_reused`)

GIVEN a note created with id `<N>`, then deleted
WHEN the client creates a new note
THEN the new note's id differs from `<N>` and from every id issued before

### S-013 — Client cannot choose or overwrite an id

**Covers:** F-002, R-004 — Coverage: `NOT_COVERED`

GIVEN an existing note `{"id": <N>, "text": "original"}`
WHEN the client sends `POST /notes` with `{"text": "intruder", "id": <N>}`
THEN `GET /notes/<N>` still returns `{"id": <N>, "text": "original"}`
AND if the request is accepted, the created note's id differs from every id issued before

### S-014 — Concurrent creations get distinct ids

**Covers:** F-002, R-003, R-009 — Coverage: `NOT_COVERED` — `KNOWN GAP` (TD-02)

GIVEN a running service
WHEN many `POST /notes` requests are sent concurrently
THEN every successful response carries a distinct id
