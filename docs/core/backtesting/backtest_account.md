# BackTestAccount

## Table of Contents
- [BackTestAccount](#back_test_account.back_test_account)
- [get_dict](#back_test_account.back_test_account.get_dict)
- [asdict](#back_test_account.asdict)
- [set_attrs](#back_test_account.set_attrs)


### BackTestAccount
<a id="back_test_account.back_test_account"></a>
```python
@dataclass
class BackTestAccount:
```
The `BackTestAccount` class provides data structure for managing account data specifically for backtesting purposes.

#### Attributes:
| Name        | Type          | Description                                               |
|-------------|---------------|-----------------------------------------------------------|
| `balance`   | `float`       | The account balance for the backtest                      |
| `equity`    | `float`       | The equity value of the account during the backtest       |
| `currency`  | `str`         | The currency type used in the backtesting account         |
| `leverage`  | `float`       | Leverage ratio applied to the backtest account            |
| `spread`    | `int`         | Spread value applied to simulated trades                  |


<a id="back_test_account.get_dict"></a>
### get_dict
```python
def get_dict(exclude: set = None, include: set = None) -> dict
```
Returns a dictionary representation of the account data. The `exclude` and `include` parameters allow filtering of data keys.

#### Arguments:
| Name      | Type  | Description                                              |
|-----------|-------|----------------------------------------------------------|
| `exclude` | `set` | A set of attribute names to exclude from the dictionary. |
| `include` | `set` | A set of attribute names to include in the dictionary.   |


<a id="back_test_account.asdict"></a>
### asdict
```python
def asdict() -> dict
```
Returns a dictionary of all attributes in the account data without filtering.


### set_attrs
<a id="back_test_account.set_attrs"></a>
```python
def set_attrs(**kwargs)
```
Sets multiple attributes at once by passing key-value pairs as keyword arguments.
