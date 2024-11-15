# Utils
Utils is a collection of utility functions that are used throughout the codebase. It is a collection of functions.

## Table of Contents
- [round_off](#_utiils.round_off)
- [dict_to_string](#_utils.dict_to_string)
- [round_down](#_utils.round_down)
- [round_up](#_utils.round_up)
- [async_cache](#_utils.async_cache)
- [backoff_decorator](#_utils.backoff_decorator)
- [error_handler](#_utils.error_handler)
- [error_handler_sync](#_utils.error_handler_sync)


<a id="_utils.round_off"></a>
### round_off
```python
def round_off(value: float, step: float, round_down: bool = True) -> float:
```
Rounds off a value to the nearest step. If round_down is True, it will round down, otherwise it will round up.

#### Parameters:
| Name       | Type  | Description                                | Default |
|------------|-------|--------------------------------------------|---------|
| value      | float | The value to round off.                    |         |
| step       | float | The step to round off to.                  |         |
| round_down | bool  | Whether to round down. If False, round up. | True    |

#### Returns:
| Type  | Description            |
|-------|------------------------|
| float | The rounded off value. |


<a id="_utils.dict_to_string"></a>
### dict_to_string
```python
def dict_to_string(data: dict, multi=True) -> str:
```
Converts a dictionary to a string. If multi is True, it will return a multi-line string.

#### Parameters:
| Name  | Type | Description                            | Default |
|-------|------|----------------------------------------|---------|
| data  | dict | The dictionary to convert to a string. |         |
| multi | bool | Whether to return a multi-line string. | True    |

#### Returns:
| Type | Description                 |
|------|-----------------------------|
| str  | The dictionary as a string. |


<a id="_utils.round_down"></a>
### round_down
```python
def round_down(value: float, base: int) -> int:
```
Rounds down a value to the nearest base. 

#### Parameters:
| Name  | Type  | Description                        |
|-------|-------|------------------------------------|
| value | float | The value to round down.           |
| base  | int   | The base to round down to.         |


<a id="_utils.round_up"></a>
### round_up
```python
def round_up(value: float, base: int) -> int:
```
Rounds up a value to the nearest base.

#### Parameters:
| Name  | Type  | Description                      |
|-------|-------|----------------------------------|
| value | float | The value to round up.           |
| base  | int   | The base to round up to.         |


<a id="_utils.async_cache"></a>
### async_cache
```python
def async_cache(func: Callable) -> Callable:
```
A decorator to cache the result of an async function.


<a id="_utils.backoff_decorator"></a>
### backoff_decorator
```python
def backoff_decorator(func=None, *, max_retries: int = 2, retries: int = 0, error="") -> Callable:
```
A decorator to retry a function with exponential backoff.

#### Parameters:
| Name        | Type | Description                                | Default |
|-------------|------|--------------------------------------------|---------|
| func        |      | The function to decorate.                  |         |
| max_retries | int  | The maximum number of retries.             | 2       |
| retries     | int  | The current number of retries.             | 0       |
| error       | str  | The error message to display on exception. |         |


<a id="_utils.error_handler"></a>
### error_handler
```python
async def error_handler(func=None, *, msg="", exe=Exception, response=None, log_error_msg=True) -> Callable:
```
A decorator to handle exceptions in an async function.

#### Parameters:
| Name          | Type | Description                                | Default |
|---------------|------|--------------------------------------------|---------|
| func          |      | The function to decorate.                  |         |
| msg           | str  | The error message to display on exception. |         |
| exe           |      | The exception to catch.                    |         |
| response      |      | The response to return on exception.       |         |
| log_error_msg | bool | Whether to log the error message.          | True    |


<a id="_utils.error_handler_sync"></a>
### error_handler_sync
```python
def error_handler_sync(func=None, *, msg="", exe=Exception, response=None, log_error_msg=True) -> Callable:
```
A decorator to handle exceptions in a sync function.
