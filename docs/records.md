# Records

## Table of contents
- [Records](#records)
- [\_\_init\_\_](#__init__)
- [get\_records](#get_records)
- [read\_update](#read_update)
- [update\_rows](#update_rows)
- [update\_records](#update_records)
- [update\_record](#update_record)
  
<a id="records"></a>
### Records
```python
class Records()
```
This utility class read trade records from csv files, and update them based on their closing positions. To use this default
implementation the csv files should at least have the following columns `['order', 'symbol', 'actual_profit', 'win', 'closed']`
Once a trade have been closed, the actual profit and win status will be updated in the csv file.
#### Headers
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
Initialize the Records class.
#### Arguments
| name         | type | description                                                    |
|--------------|------|----------------------------------------------------------------|
| records_dir  | Path | Absolute path to directory containing record of placed trades. |

<a id="get_records"></a>
### get\_records
```python
async def get_records()
```
Get trade records from records_dir folder
#### Yields
| type | description        |
|------|--------------------|
| Path | Trade record files |

<a id="read_update"></a>
### read\_update
```python
async def read_update(file: Path)
```
Read and update trade records
#### Arguments
| name | type | description       |
|------|------|-------------------|
| file | Path | Trade record file |

<a id="update_rows"></a>
### update\_rows
```python
async def update_rows(rows: list[dict]) -> list[dict]
```
Update the rows of entered trades in the csv file with the actual profit.
#### Arguments
| name | type       | description                                                               |
|------|------------|---------------------------------------------------------------------------|
| rows | list[dict] | A list of dictionaries from the dictionary writer object of the csv file. |

#### Returns
| type       | description                                                   |
|------------|---------------------------------------------------------------|
| list[dict] | A list of dictionaries with the actual profit and win status. |


<a id="update_records"></a>
### update\_records
```python
async def update_records()
```
Update trade records in the records_dir folder.

<a id="update_record"></a>
### update\_record
```python
async def update_record(file: Path | str)
```
Update a single trade record file.
