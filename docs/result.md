<a id="aiomql.result"></a>

# aiomql.result

<a id="aiomql.result.Result"></a>

## Result Objects

```python
class Result()
```

A base class for handling trade results and strategy parameters for record keeping and reference purpose.
The data property must be implemented in the subclass

**Attributes**:

- `config` _Config_ - The configuration object
- `name` - Any desired name for the result file object

<a id="aiomql.result.Result.__init__"></a>

#### \_\_init\_\_

```python
def __init__(result: OrderSendResult, parameters: dict = None, name: str = '')
```

Prepare result data

**Arguments**:

  result:
  parameters:
  name:

<a id="aiomql.result.Result.to_csv"></a>

#### to\_csv

```python
async def to_csv()
```

Record trade results and associated parameters as a csv file

<a id="aiomql.result.Result.save_csv"></a>

#### save\_csv

```python
async def save_csv()
```

Save trade results and associated parameters as a csv file in a separate thread

