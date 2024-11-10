# Risk Assessment and Management

## Table of Contents
- [RAM](#ram.ram)
- [\__init\__](#ram.__init__)
- [get_amount](#ram.get_amount)
- [check_losing_positions](#ram.check_losing_positions)
- [check_open_positions](#ram.check_open_positions)

<a id="ram.ram"></a>
### RAM
```python
class RAM
```
Risk Assessment and Management. You can customize this class based on how you want to manage risk.

#### Attributes:
| Name             | Type      | Description                                       | Default   |
|------------------|-----------|---------------------------------------------------|-----------|
| `account`        | `Account` | The account object                                | Account() |
| `risk_to_reward` | `float`   | Risk to reward ratio                              | 2         |
| `risk`           | `float`   | Percentage of account balance to risk per trade   | 1%        |
| `fixed_amount`   | `float`   | A fixed amount to risk per trade                  |           |
| `min_amount`     | `float`   | Minimum amount to risk per trade                  |           |
| `max_amount`     | `float`   | Maximum amount to risk per trade                  |           |
| `loss_limit`     | `int`     | Number of open losing trades to allow at any time | 3         |
| `open_limit`     | `int`     | Number of open trades to allow at any time        | 3         |


<a id="ram.__init__"></a>
### \_\_init\_\_
```python
def __init__(self, **kwargs):
```
Risk Assessment and Management. All provided keyword arguments are set as attributes.
#### Parameters
| Name             | Type   | Description                                        | Default   |
|------------------|--------|----------------------------------------------------|-----------|
| `kwargs`         | `dict` | Keyword arguments to be set as instance attributes | {}        |


<a id="ram.get_amount"></a>
### ram.get_amount
```python
async def get_amount() -> float
```
Calculate the amount to risk per trade as a percentage of balance.

#### Returns:
| Type    | Description                                           |
|---------|-------------------------------------------------------|
| `float` | Amount to risk per trade in terms of account currency |

<a id="ram.check_losing_positions"></a>
### check_losing_positions
```python
async def check_losing_positions(self) -> bool:
```
Check if the number of open losing trades is greater than or equal to the loss limit.

#### Returns:
| Type   | Description                                                                           |
|--------|---------------------------------------------------------------------------------------|
| `bool` | True if the number of open losing trades is more than the loss limit, False otherwise |


<a id="ram.check_open_positions"></a>
### check_open_positions
```python
async def check_open_positions(self) -> bool:
```
Check if the number of open positions is less than or equal the loss limit.

#### Returns:
| Type   | Description                                                                           |
|--------|---------------------------------------------------------------------------------------|
| `bool` | True if the number of open losing trades is more than the loss limit, False otherwise |
