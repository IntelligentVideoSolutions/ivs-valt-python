# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`ivs-valt-python` is a Python library that wraps the VALT lecture-capture API (v5 and v6). It is consumed by other IVS projects; there is no runnable entry point here.

## Syntax checking

There is no test suite or build system. Use `py_compile` to verify files parse cleanly after edits:

```bash
python -m py_compile valt/mixins/<file>.py
```

## Architecture

The public surface is the single `VALT` class (`valt/valt.py`). It is assembled entirely via Python multiple inheritance from a set of single-responsibility mixins in `valt/mixins/`:

| Mixin | Responsibility |
|---|---|
| `valt_communication` | `send_to_valt()` — all HTTP (GET/POST/multipart) |
| `valt_log` | Logger setup; Kivy-aware |
| `valt_auth` | `auth()`, `reauthenticate()`, `accesstoken` observable property |
| `valt_errors` | `handleerror()` — maps exception strings to user-facing `errormsg` |
| `valt_monitor` | Background thread polling `selected_room` status |
| `valt_room` | Room recording control (start/stop/pause/resume/lock/unlock) |
| `valt_admin` | Server-level queries (rooms, cameras, users, schedule, version) |
| `valt_recording` | Upload/download/query recordings |
| `valt_users` | User lookup by card number, VALT-version-aware |
| `valt_groups` | User group info and editing |
| `valt_preset` | Camera preset CRUD |
| `valt_comment` | Recording comment CRUD |

Every mixin uses `from __future__ import annotations` and the `TYPE_CHECKING` guard to reference `VALT` in type hints without a circular import:

```python
if TYPE_CHECKING:
    from ..valt import VALT

class valt_foo:
    def bar(self: VALT, ...):
```

## Key conventions

**Return values:** Methods return `0` on failure and the relevant data (dict, list, id, string) on success. Do not return `None` as a failure sentinel — always `return 0`.

**Authentication guard:** Every method that calls the API must begin with:
```python
if self.accesstoken == 0:
    self.logger.error(__name__ + ": " + "Not Currently Authenticated to VALT")
```
`accesstoken == 0` means unauthenticated. On any HTTP error, `send_to_valt()` resets `accesstoken` to `0`.

**Observable properties:** Three properties fire registered callbacks on change — bind with the corresponding `bind_to_*` method:
- `errormsg` — human-readable error string; `None` when no error
- `accesstoken` — `0` when unauthenticated
- `selected_room_status` — integer (1=available, 2=recording, 3=paused, 4=locked, 5=prepared, 99=unknown)

**Background threads:** `__init__` starts two daemon threads automatically:
1. A `reauthenticate` timer (fires every 28800 s on success, 30 s on failure)
2. A `check_room_status` loop (polls `selected_room` every `room_check_interval` seconds)

Call `disconnect()` to stop both before discarding the object.

**VALT version branching:** After auth, `self.version`, `self.major_version`, and `self.minor_version` are populated. Methods that differ between v5 and v6 branch on `self.major_version`. The `get_user_by_card_number` in `users.py` is the canonical example.

**`send_to_valt` contract:** Returns a parsed dict/list on success, or `None` (implicitly) if any exception is caught. Always check the return type before indexing:
```python
if type(data).__name__ == "dict":   # legacy style used throughout
if isinstance(data, dict):          # preferred going forward
```

