# Risk Assessment and Management

## Table of Contents
- [RAM](#RAM)
- [\_\_init\_\_](#__init__)
- [get\_amount](#get_amount)
- [check_losing_positions](#check_losing_positions)
- [check_balance_level](#check_balance_level)

<a id="RAM"></a>
### RAM
```python
class RAM
```
Risk Assessment and Management. You can customize this class based on how you want to manage risk.
#### Attributes
| Name             | Type    | Description                                          | Default |
|------------------|---------|------------------------------------------------------|---------|
| `risk_to_reward` | `float` | Risk to reward ratio                                 | 1       |
| `risk`           | `float` | Percentage of account balance to risk per trade      |         |
| `points`         | `float` | A fixed number of points per trade can be fixed here |         |
| `pips`           | `float` | A fixed number of pips per trade can be fixed here   |         |
| `min_amount`     | `float` | Minimum amount to risk per trade                     |         |
| `max_amount`     | `float` | Maximum amount to risk per trade                     |         |
| `balance_level`  | `float` | Ratio of margin to available balance as a percentage | 10      |
| `loss_limit`     | `int`   | Number of open losing trades to allow at any time    | 3       |

<a id="__init__"></a>
### \_\_init\_\_
```python
def __init__(self, *, risk_to_reward: float = 1, risk: float = 0.01, **kwargs):
```
Risk Assessment and Management. All provided keyword arguments are set as attributes.
#### Parameters
| Name             | Type    | Description                                        | Default   |
|------------------|---------|----------------------------------------------------|-----------|
| `risk_to_reward` | `float` | Risk to reward ratio                               | 1         |
| `risk`           | `float` | Percentage of account balance to risk per trade    | 0.01 # 1% |
| `kwargs`         | `Dict`  | Keyword arguments to be set as instance attributes | {}        |


<a id="get_amount"></a>
### get\_amount
```python
async def get_amount() -> float
```
Calculate the amount to risk per trade as a percentage of balance.
#### Returns
| Type   | Description                                           |
|--------|-------------------------------------------------------|
|  float | Amount to risk per trade in terms of account currency |

<a id="check_losing_positions"></a>
### check_losing_positions
```python
async def check_losing_positions(self) -> bool:
```
Check if the number of open losing trades is greater than or equal to the loss limit.
#### Returns
| Type | Description                                                                           |
|------|---------------------------------------------------------------------------------------|
| bool | True if the number of open losing trades is more than the loss limit, False otherwise |

<a id="check_balance_level"></a>
### check\_balance\_level
```python
async def check_balance_level(self) -> bool:
```
Check if the balance level is greater than or equal to the fixed balance level.
#### Returns
| Type | Description                                                                     |
|------|---------------------------------------------------------------------------------|
| bool | True if the balance level is more than the fixed balance level, False otherwise |
