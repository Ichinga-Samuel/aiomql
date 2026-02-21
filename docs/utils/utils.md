# utils

`aiomql.utils.utils` — Decorators, rounding, and async caching.

## Overview

General-purpose utility functions used throughout the library: error-handling
decorators, a ceiling-rounding helper, and an async-friendly cache decorator.

## Functions

### `round_up(value, decimals=0)`

> Rounds a number **up** to the specified decimal places.

Uses `decimal.ROUND_UP` for precise ceiling rounding.

**Args:**
- `value` (`float`) — The value to round.
- `decimals` (`int`) — Decimal places. Defaults to `0`.

**Returns:** `float`

---

### `async_cache(fn)`

> Decorator that caches the result of an async function.

Wraps an `async def` function so that subsequent calls with the same arguments
return the cached result without re-executing the coroutine.

---

### `error_handler(func=None, *, msg="", tb=False, …)`

> Decorator for uniform exception handling.

Catches exceptions, logs them (optionally with traceback), and returns a
fallback value instead of re-raising.

---

### `backoff_retry(func=None, *, retries=3, error=Exception, …)`

> Decorator that retries a function with exponential back-off.

Retries the decorated function `retries` times on failure, with increasing
delays between attempts.

---

### `dict_to_string(data)`

> Converts a dictionary to a formatted key=value string.
