# Result

## Table of Contents
- [Result](#result.result)
- [__init__](#result.__init__)
- [save](#result.save)
- [get_data](#result.get_data)
- [to_csv](#result.to_csv)
- [to_json](#result.to_json)


<a id="result.result"></a>
```python
class Result
```
A base class for handling trade results and strategy parameters for record keeping and analysis.
#### Attributes:
| Name         | Type              | Description                       |
|--------------|-------------------|-----------------------------------|
| `result`     | `OrderSendResult` | The result of the trade           |
| `parameters` | `dict`            | The parameters used for the trade |
| `name`       | `str`             | The name of the result object     |


<a id="result.__init__"></a>
### \__init\__
```python
def __init__(*, result: OrderSendResult, parameters: dict = None, name: str = '')
```
Prepare result data for record keeping and analysis.

#### Parameters:
| Name         | Type              | Description                       |
|--------------|-------------------|-----------------------------------|
| `result`     | `OrderSendResult` | The result of the trade           |
| `parameters` | `dict`            | The parameters used for the trade |
| `name`       | `str`             | The name of the result object     |


<a id="result.get_data"></a>
### get_data
```python
def get_data(self) -> dict
```
Get the result data as a dictionary

#### Returns:
| Type   | Description     |
|--------|-----------------|
| `dict` | The result data |


<a id="result.to_save"></a>
### to_save
```python
async def to_save(*, trade_record_mode: Literal["csv", "json"] = None)
```
Save to json or csv depending on the trade record mode.

#### Returns:
| Name                | Type                     | Description           | Default |
|---------------------|--------------------------|-----------------------|---------|
| `trade_record_mode` | `Literal["csv", "json"]` | The trade record mode | None    |


<a id="result.to_csv"></a>
### to_csv
```python
async def to_csv()
```
Record trade results and associated parameters as a csv file


<a id="result.to_json"></a>
### to_json
```python
async def to_json()
```
Record trade results and associated parameters as a json file
```
