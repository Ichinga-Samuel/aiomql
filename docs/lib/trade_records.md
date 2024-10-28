# Trade Records

## Table of contents
- [Trade Records](#trade_records)
- [\_\_init\_\_](#__init__)
- [get_csv_records](#get_csv_records)
- [get_json_records](#get_json_records)
- [read_update_csv](#read_update_csv)
- [read_update_json](#read_update_json)
- [update_rows](#update_rows)
- [update_row](#update_row)
- [update_csv_records](#update_csv_records)
- [update_json_records](#update_json_records)
- [update_csv_record](#update_csv_record)
- [update_json_record](#update_json_record)

<a id="trade_records"></a>
### Trade Records
```python
class TradeRecords()
```
This utility class read trade records from csv and json files, and update them based on their closing positions.
To use this default implementation the csv or json file should be able to provide the following data.
`['order', 'symbol', 'actual_profit', 'win', 'closed']`
Once a trade have been closed, the actual profit and win status will be updated in the csv file.

#### Default Headers
| column        | type  | description                                           |
|---------------|-------|-------------------------------------------------------|
| order         | int   | Order id of the trade                                 |
| symbol        | str   | the name of the Symbol                                |
| actual_profit | float | The actual profit of the trade, this zero by default  |
| win           | bool  | The win status of the trade, this is False by default |
| closed        | bool  | The status of the trade, this is False by default     |

#### Attributes
| name        | type   | description                                                  |
|-------------|--------|--------------------------------------------------------------|
| records_dir | Path   | Absolut path to directory containing record of placed trades |
| config      | Config | Config object                                                |

<a id="__init__"></a>
### \_\_init\_\_
```python
def __init__(records_dir: Path | str = '')
```
Initialize an instance of the class.
#### Parameters
| name         | type | description                                                    |
|--------------|------|----------------------------------------------------------------|
| records_dir  | Path | Absolute path to directory containing record of placed trades. |

<a id="get_csv_records"></a>
### get_csv_records
```python
async def get_csv_records()
```
Get trade records from records_dir folder.
#### Yields
| type | description        |
|------|--------------------|
| Path | Trade record files |

<a id="get_json_records"></a>
### get_json_records
```python
async def get_json_records()
```
Get trade records from records_dir folder.
#### Yields
| type | description        |
|------|--------------------|
| Path | Trade record files |

<a id="read_update_csv"></a>
### read_update_csv
```python
async def read_update_csv(file: Path)
```
Read and update trade records from a csv file.
#### Parameters
| name | type | description       |
|------|------|-------------------|
| file | Path | Trade record file |

<a id="read_update_json"></a>
### read_update_json
```python
async def read_update_json(file: Path)
```
Read and update trade records from a json file.
#### Parameters
| name | type | description       |
|------|------|-------------------|
| file | Path | Trade record file |

<a id="update_rows"></a>
### update_rows
```python
async def update_rows(rows: list[dict]) -> list[dict]
```
Update the rows of entered trades with the actual profit.
#### Parameters
| name | type       | description                                                               |
|------|------------|---------------------------------------------------------------------------|
| rows | list[dict] | A list of dictionaries from the dictionary writer object of the csv file. |

#### Returns
| type       | description                                                   |
|------------|---------------------------------------------------------------|
| list[dict] | A list of dictionaries with the actual profit and win status. |

<a id="update_row"></a>
### update_row
```python
async def update_row(row: dict) -> dict
```
Update the row of an entered trade with the actual profit.
#### Parameters
| name | type | description                               |
|------|------|-------------------------------------------|
| row  | dict | A dictionary from the csv file row object |

#### Returns
| type | description                        |
|------|------------------------------------|
| dict | A dictionary with the actual profit |
