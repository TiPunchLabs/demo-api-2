# demo-api-2 — FlowForge spec review

> Working document behind `SPEC.md`; it does not replace it.
> Analysis: 2026-10-19, `main` @ `a5eb53a`. Owner decisions applied the same day.

------

## Sources analysed

| Source | What it provided |
|---|---|
| `README.md` § API | Endpoint table, note shape, 1–500 char text, ascending list order, 404/422 cases |
| `CLAUDE.md` | Purpose (FlowForge target), intentional in-memory storage, fresh store per app, scope constraints |
| Issue #1 (closed) | Owner-approved delete behaviour, exact 404 body, ids never reused, 422 on non-integer id |
| `src/demo_api_2/routes/*.py`, `schemas.py`, `storage.py` | Implemented endpoints, status codes, text constraint, id counter, ordering |
| `tests/test_health.py`, `tests/test_notes.py` | 9 tests — behaviour actually locked in |
| Git history (3 commits, PR #2) | Scaffold + delete feature |
| Read-only runtime probes (in-process `TestClient`) | Edge cases not covered by tests |
| Owner decisions Q-01…Q-06 (2026-10-19) | See decisions log |

No `SPEC.md`, `AGENTS.md`, `docs/` or ADR existed before this analysis.

------

## Owner decisions (2026-10-19)

| # | Question | Decision | Reflected in |
|---|---|---|---|
| Q-01 | Whitespace-only text? | Rejected: a note needs ≥ 1 non-whitespace char, 1–500 limit kept. No code change in this task | R-002, S-005, TD-01 |
| Q-02 | Id contract? | Unique, server-assigned, never reused; clients must not control assignment. Start-at-1 / +1 and silent ignoring of a client `id` are **not** contractual | R-003, R-004, S-012, S-013 |
| Q-03 | 422 on `GET /notes/{id}` | Document it in README | README, R-007 |
| Q-04 | Concurrency | Concurrent creations must keep ids unique. No locking in this task; gap recorded as debt | R-009, S-014, TD-02 |
| Q-05 | Maintaining `SPEC.md` | `SPEC.md` is the functional source of truth, README stays user-facing; CLAUDE.md updated | CLAUDE.md |
| Q-06 | No update endpoint | Intentional for the current scope; future features may add it | SPEC § 1 |

------

## Confirmed requirements

All rules R-001…R-009 of `SPEC.md` are `CONFIRMED` (README, CLAUDE.md, Issue #1 or owner
decision). Two of them are not met by the current code — see technical debt.

## Observed behaviours, not contractual

| Behaviour | Evidence | Status |
|---|---|---|
| Ids start at `1`, increment by 1 | `storage.py`; asserted by tests | implementation detail (Q-02) |
| Unknown payload fields, including `id`, silently ignored | probe `{"text":"x","id":99}` → `201` | implementation detail (Q-02) |
| No search / filtering / pagination | code | current state, not decided |
| No authentication | code | current state, not decided |
| `GET /notes/` → `307` redirect; ids `0`/negative → `404` | probes; FastAPI defaults | left out of SPEC (framework detail) |

------

## Contradictions

| # | Gap | Resolution |
|---|---|---|
| C-01 | README `GET /notes/{id}` row omitted the `422` | Fixed in README (Q-03) |
| C-02 | 500/501 boundary documented but untested | Coverage gap — see below |
| C-03 | CLAUDE.md did not require maintaining `SPEC.md` | Fixed in CLAUDE.md (Q-05) |
| C-04 | R-002 (whitespace rejected) vs code (accepted) | Open — TD-01 |
| C-05 | R-009 (concurrent uniqueness) vs code (no synchronisation) | Open — TD-02 |
| C-06 | Tests assert concrete ids (`1`, `2`), stricter than the R-004 contract | Accepted: tests describe the current implementation; a future change of id scheme must update them through its Issue, not weaken them silently |

README's `POST /notes` row still says `1–500 chars` without the non-whitespace rule: README
describes actual behaviour, and it will be updated by the Issue that fixes TD-01.

------

## Technical debt

- **TD-01 — Whitespace-only text accepted.** `NoteIn.text` only enforces length; `"   "` →
  `201`. Violates R-002 / S-005. Fix: an Issue adding the validation, a test for S-005 and the
  README wording.
- **TD-02 — Id assignment is not concurrency-safe.** `NoteStore.create` reads and increments
  `_next_id` without a lock, while FastAPI runs sync endpoints in a threadpool. A duplicate id is
  possible in theory (read from code, not reproduced). Violates R-009 / S-014. Fix: an Issue
  adding synchronisation (or an atomic counter) and a concurrency test.

------

## Test coverage gaps

| Scenario | Status | Missing |
|---|---|---|
| S-004 Invalid text | partial | missing `text`, non-string `text`, 501 chars |
| S-005 Whitespace-only rejected | none | test — will fail until TD-01 is fixed |
| S-006 500 chars accepted | none | boundary test |
| S-007 List order | none | multi-note ordering test |
| S-011 Malformed id | partial | `GET /notes/abc` → 422 |
| S-013 Client cannot control id | none | `POST` with an existing `id` |
| S-014 Concurrent creations | none | concurrency test — may fail until TD-02 is fixed |

Fully covered: S-001, S-002, S-003, S-008, S-009, S-010, S-012.

Suggested follow-up Issues: (1) tests-only for S-004, S-006, S-007, S-011, S-013;
(2) TD-01 with S-005; (3) TD-02 with S-014.

------

## Unresolved questions

- **Q-07 — Status code for whitespace-only text.** R-002 states `422`, by consistency with the
  other text validation errors; the owner decision said "rejected" without a code. Confirm
  when the TD-01 Issue is refined.
- **Q-08 — Client-supplied `id`.** Ignore it (current) or reject the request? Both satisfy
  R-004; to settle only if a future Issue needs it.

------

## Recommendation

`SPEC.md` covers 5 features, 9 rules and 14 scenarios; every feature has at least one scenario,
contractual rules and implementation details are separated, and the two requirements the code
does not meet are tagged `KNOWN GAP`.

**Verdict: READY_FOR_REVIEW** — owner review of the PR is the remaining step before `SPEC.md`
becomes the official reference for FlowForge agents.
