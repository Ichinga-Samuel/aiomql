# sessions

`aiomql.lib.sessions` — Trading session time windows.

## Overview

Provides `Session` (a single trading window) and `Sessions` (a collection of windows)
for restricting trading to specific hours of the day. Sessions can automatically trigger
actions at their boundaries — e.g. closing all positions when a session ends.

## Classes

### `Session`

> Defines a single trading time window.

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Session name |
| `start` | `time` | Session start time |
| `end` | `time` | Session end time |
| `on_start` | `Callable \| None` | Hook called when the session opens |
| `on_end` | `Callable \| None` | Hook called when the session closes |
| `close_all` | `bool` | If `True`, close all positions on session end |

#### Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `duration` | `timedelta` | Length of the session |
| `in_session` | `bool` | `True` if current time is within the window |

---

### `Sessions`

> Manages multiple `Session` objects.

| Attribute | Type | Description |
|-----------|------|-------------|
| `sessions` | `list[Session]` | Registered sessions |

#### Methods

| Method | Description |
|--------|-------------|
| `add(session)` | Adds a session |
| `find(name)` | Finds a session by name |
| `check()` | Checks which sessions are active and triggers hooks |

## Synchronous API

Available in `aiomql.lib.sync.sessions`.
