# Trade Records

## Table of contents
- [Trade Records](#trade_records)
- [\_\_init\_\_](#trade_records.__init__)
- [get_csv_records](#trade_records.get_csv_records)
- [get_json_records](#trade_records.get_json_records)
- [read_update_csv](#trade_records.read_update_csv)
- [read_update_json](#trade_records.read_update_json)
- [update_rows](#trade_records.update_rows)
- [update_row](#trade_records.update_row)
- [update_csv_records](#trade_records.update_csv_records)
- [update_json_records](#trade_records.update_json_records)
- [update_csv_record](#trade_records.update_csv_record)
- [update_json_record](#trade_records.update_json_record)

<a id="trade_records.trade_records"></a>
### Trade Records
```python
class TradeRecords()
```
This utility class read trade records from csv and json files, and update them based on their closing positions.
Once a trade have been closed, the actual profit and win status will be updated in the file.

#### Attributes:
| name          | type     | description                               |
|---------------|----------|-------------------------------------------|
| `config`      | `Config` | Config object                             |
| `records_dir` | `Path`   | A directory for finding the trade records |

<a id="trade_records.__init__"></a>
### \__init\__
```python
def __init__(*, records_dir: Path | str = '')
```
Initialize an instance of the class.

#### Parameters:
| name          | type   | description                                                    |
|---------------|--------|----------------------------------------------------------------|
| `records_dir` | `Path` | Absolute path to directory containing record of placed trades. |


<a id="trade_records.get_csv_records"></a>
### get_csv_records
```python
async def get_csv_records()
```
Get trade records from records_dir folder.

#### Yields:
| type | description        |
|------|--------------------|
| Path | Trade record files |


<a id="trade_records.get_json_records"></a>
### get_json_records
```python
async def get_json_records()
```
Get trade records from records_dir folder.

#### Yields
| type | description        |
|------|--------------------|
| Path | Trade record files |


<a id="trade_records.read_update_csv"></a>
### read_update_csv
```python
async def read_update_csv(*, file: Path)
```
Read and update trade records from a csv file.

#### Parameters:
| name   | type   | description       |
|--------|--------|-------------------|
| `file` | `Path` | Trade record file |


<a id="trade_records.read_update_json"></a>
### read_update_json
```python
async def read_update_json(*, file: Path)
```
Read and update trade records from a json file.

#### Parameters:
| name   | type   | description       |
|--------|--------|-------------------|
| `file` | `Path` | Trade record file |


<a id="trade_records.update_rows"></a>
### update_rows
```python
async def update_rows(*, rows: list[dict]) -> list[dict]
```
Update the rows of entered trades with the actual profit.

#### Parameters:
| name   | type         | description                                                               |
|--------|--------------|---------------------------------------------------------------------------|
| `rows` | `list[dict]` | A list of dictionaries from the dictionary writer object of the csv file. |

#### Returns:
| Type         | Description                                                   |
|--------------|---------------------------------------------------------------|
| `list[dict]` | A list of dictionaries with the actual profit and win status. |


<a id="trade_records.update_row"></a>
### update_row
```python
async def update_row(row: dict) -> dict
```
Update the row of an entered trade with the actual profit.

#### Parameters:
| Name  | Type   | Description                               |
|-------|--------|-------------------------------------------|
| `row` | `dict` | A dictionary from the csv file row object |

#### Returns:
| Type | Description                         |
|------|-------------------------------------|
| dict | A dictionary with the actual profit |


<a id="trade_records.update_csv_record"></a>
### update_csv_record
```python
async def update_csv_record(*, file: Path | str)
```
Update a single trade record csv file

#### Parameters:
| Name   | Type   | Description             |
|--------|--------|-------------------------|
| `file` | `Path` | A trade record csv file |


<a id="trade_records.update_csv_records"></a>
### update_csv_records
```python
def update_csv_records()
```
Update csv trade records in the records_dir folder.


<a id="trade_records.update_json_record"></a>
### update_csv_record
```python
async def update_json_record(*, file: Path | str)
```
Update a single trade record json file

#### Parameters:
| Name   | Type   | Description              |
|--------|--------|--------------------------|
| `file` | `Path` | A trade record json file |


<a id="trade_records.update_json_records"></a>
### update_json_records
```python
def update_json_records()
```
Update json trade records in the records_dir folder.
