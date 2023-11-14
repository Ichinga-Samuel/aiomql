## <a id="ram"></a> Risk Assessment and Management

```python
class RAM()
```
### \_\_init\_\_

```python
def __init__(**kwargs)
```
Risk Assessment and Management. All provided keyword arguments are set as attributes.

#### Parameters
| Name           | Type | Description                                           | Default |
|----------------|------|-------------------------------------------------------|---------|
| risk_to_reward | float | Risk to reward ratio                                  | 1|
| risk           | float | Percentage of account balance to risk per trade       | 0.01 # 1%|
| amount         | float | Amount to risk per trade in terms of account currency | 0|
| **kwargs**     | Dict | Keyword arguments to be set as object attributes      | {} |


<a id="aiomql.ram.RAM.get_amount"></a>

### get\_amount

```python
async def get_amount(risk: float = 0) -> float
```
Calculate the amount to risk per trade as a percentage of free margin.

#### Parameters
| Name           | Type | Description                                           | Default |
|----------------|------|-------------------------------------------------------|---------|
| risk           | float | Percentage of account balance to risk per trade       | 0.01 # 1%|

#### Returns
| Name           | Type | Description                                           |
|----------------|------|-------------------------------------------------------|
| amount         | float | Amount to risk per trade in terms of account currency |
