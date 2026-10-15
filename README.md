# demo-api-2

Minimal FastAPI notes service. Second target repository of
[FlowForge](https://github.com/TiPunchLabs/flowforge), used to validate multi-project /
multi-repository operation. Storage is in memory.

## Usage

```bash
uv sync
uv run demo-api-2          # http://127.0.0.1:8000 (docs: /docs)
uv run pytest
```

## API

| Method | Path | Body | Success | Errors |
|---|---|---|---|---|
| `GET` | `/health` | — | `200 {"status": "ok"}` | — |
| `GET` | `/notes` | — | `200` list of notes, ascending id | — |
| `GET` | `/notes/{id}` | — | `200` the note | `404` unknown id |
| `POST` | `/notes` | `{"text": str}` (1–500 chars) | `201` the note with its `id` | `422` invalid body |

A note is `{"id": int, "text": str}`.
