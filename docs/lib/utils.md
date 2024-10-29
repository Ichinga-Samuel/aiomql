# Utils
Utils is a collection of utility functions that are used throughout the codebase. It is a collection of functions.

## Table of Contents
- [round_off](#round_off)
- [find_bearish_fractal](#find_bearish_fractal)
- [find_bullish_fractal](#find_bullish_fractal)
- [dict_to_string](#dict_to_string)

<a id="round_off"></a>
```python
def round_off(value: float, step: float, round_down: bool = True) -> float:
```
Rounds off a value to the nearest step. If round_down is True, it will round down, otherwise it will round up.
#### Parameters
| Name       | Type  | Description                                | Default |
|------------|-------|--------------------------------------------|---------|
| value      | float | The value to round off.                    |         |
| step       | float | The step to round off to.                  |         |
| round_down | bool  | Whether to round down. If False, round up. | True    |
#### Returns
| Type  | Description            |
|-------|------------------------|
| float | The rounded off value. |

```python
def find_bearish_fractal(candles: Candles) -> Candle | None:
```
Finds the most recent bearish fractal in the candles.
#### Parameters
| Name    | Type    | Description                      | Default |
|---------|---------|----------------------------------|---------|
| candles | Candles | The candles to search for.       |         |
#### Returns
| Type   | Description                      |
|--------|----------------------------------|
| Candle | The most recent bearish fractal. |

```python
def find_bullish_fractal(candles: Candles) -> Candle | None:
```
Finds the most recent bullish fractal in the candles.
#### Parameters
| Name    | Type    | Description                      | Default |
|---------|---------|----------------------------------|---------|
| candles | Candles | The candles to search for.       |         |
#### Returns
| Type   | Description                      |
|--------|----------------------------------|
| Candle | The most recent bullish fractal. |

<a id="dict_to_string"></a>
```python
def dict_to_string(data: dict, multi=True) -> str:
```
Converts a dictionary to a string. If multi is True, it will return a multi-line string.
#### Parameters
| Name  | Type | Description                            | Default |
|-------|------|----------------------------------------|---------|
| data  | dict | The dictionary to convert to a string. |         |
| multi | bool | Whether to return a multi-line string. | True    |

#### Returns
| Type | Description                 |
|------|-----------------------------|
| str  | The dictionary as a string. |
