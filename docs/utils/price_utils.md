# price_utils

`aiomql.utils.price_utils` — Percentage-based price calculations.

## Overview

Utility functions for common percentage and price-range calculations used in
trading logic.

## Functions

### `price_diff(price1, price2)`

> Calculates the absolute difference between two prices.

**Returns:** `float`

---

### `price_diff_pct(price1, price2)`

> Percentage difference between two prices relative to `price1`.

**Returns:** `float` — percentage

---

### `position_in_range(value, low, high)`

> Calculates where a value falls within a range as a percentage.

**Returns:** `float` — `0.0` at `low`, `100.0` at `high`.

---

### `pct_increase(value, pct)`

> Increases a value by a percentage.

**Returns:** `float`

---

### `pct_decrease(value, pct)`

> Decreases a value by a percentage.

**Returns:** `float`

---

### `pct_of(value, pct)`

> Returns a percentage of a value.

**Returns:** `float`

---

### `price_pct_change(open_price, close_price)`

> Percentage change from `open_price` to `close_price`.

**Returns:** `float`
