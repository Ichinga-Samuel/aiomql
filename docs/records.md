<a id="aiomql.records"></a>

# aiomql.records

This module contains the Records class, which is used to read and update trade records from csv files.

<a id="aiomql.records.Records"></a>

## Records Objects

```python
class Records()
```

This utility class read trade records from csv files, and update them based on their closing positions.

**Attributes**:

- `config` - Config object
- `records_dir(Path)` - Path to directory containing record of placed trades, If not given takes the default
  from the config

<a id="aiomql.records.Records.__init__"></a>

#### \_\_init\_\_

```python
def __init__(records_dir: Path = '')
```

Initialize the Records class.

**Arguments**:

- `records_dir` _Path_ - Path to directory containing record of placed trades.

<a id="aiomql.records.Records.get_records"></a>

#### get\_records

```python
async def get_records()
```

Get trade records from records_dir folder

**Yields**:

- `files` - Trade record files

<a id="aiomql.records.Records.read_update"></a>

#### read\_update

```python
async def read_update(file: Path)
```

Read and update trade records

**Arguments**:

- `file` - Trade record file

<a id="aiomql.records.Records.update_rows"></a>

#### update\_rows

```python
async def update_rows(rows: list[dict]) -> list[dict]
```

Update the rows of entered trades in the csv file with the actual profit.

**Arguments**:

- `rows` - A list of dictionaries from the dictionary writer object of the csv file.
  

**Returns**:

- `list[dict]` - A list of dictionaries with the actual profit and win status.

<a id="aiomql.records.Records.update_records"></a>

#### update\_records

```python
async def update_records()
```

Update trade records in the records_dir folder.

<a id="aiomql.records.Records.update_record"></a>

#### update\_record

```python
async def update_record(file: Path | str)
```

Update a single trade record file.

