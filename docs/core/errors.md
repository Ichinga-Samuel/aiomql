# Errors

## Tabel of contents
- [Error](#errors.error)
- [is_connection_error](#errors.is_connection_error)


<a id="errors.error"></a>
## Error
```python
class Error
```
Error class for handling errors.

#### Attributes:
| Name           | Type         | Description                                  |
|----------------|--------------|----------------------------------------------|
| `code`         | `int`        | Error code                                   |
| `description`  | `str`        | Error description                            |
| `descriptions` | `dict`       | A dictionary of error codes and descriptions |
| `conn_errors`  | `tuple[int]` | A tuple of connection errors                 |


<a id="errors.is_connection_error"></a>
## is_connection_error
```python
def is_connection_error(self) -> bool
```
Check if an error is a connection error.

#### Returns:
| Type   | Description                                          |
|--------|------------------------------------------------------|
| `bool` | True if error is a connection error, False otherwise |
