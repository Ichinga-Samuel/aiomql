# Result

## Table of Contents
- [Result](#result)
- [__init__](#__init__)
- [get_data](#get_data)
- [to_csv](#to_csv)

<a id="result"></a>
```python
class Result()
```
A base class for handling trade results and strategy parameters for record keeping and analysis.
#### Attributes
| Name         | Type              | Description                       |
|--------------|-------------------|-----------------------------------|
| `result`     | `OrderSendResult` | The result of the trade           |
| `parameters` | `dict`            | The parameters used for the trade |
| `name`       | `str`             | The name of the result object     |


<a id="__init__"></a>
### \_\_init\_\_
```python
def __init__(result: OrderSendResult, parameters: dict = None, name: str = '')
```
Prepare result data for record keeping and analysis.
#### Parameters
| Name         | Type              | Description                       |
|--------------|-------------------|-----------------------------------|
| `result`     | `OrderSendResult` | The result of the trade           |
| `parameters` | `dict`            | The parameters used for the trade |
| `name`       | `str`             | The name of the result object     |

<a id="get_data"></a>
```python
def get_data(self) -> dict:
```
Get the result data as a dictionary
#### Returns
| Type   | Description     |
|--------|-----------------|
| `dict` | The result data |

<a id="to_csv"></a>
### to\_csv
```python
async def to_csv()
```
Record trade results and associated parameters as a csv file
