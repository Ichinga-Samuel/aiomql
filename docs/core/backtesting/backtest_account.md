# Table of Contents

* [backtest\_account](#backtest_account)
  * [BackTestAccount](#backtest_account.BackTestAccount)
    * [get\_dict](#backtest_account.BackTestAccount.get_dict)
    * [asdict](#backtest_account.BackTestAccount.asdict)
    * [set\_attrs](#backtest_account.BackTestAccount.set_attrs)

<a id="backtest_account"></a>

# backtest\_account

<a id="backtest_account.BackTestAccount"></a>

## BackTestAccount Objects

```python
@dataclass
class BackTestAccount()
```

Account data for backtesting

<a id="backtest_account.BackTestAccount.get_dict"></a>

#### get\_dict

```python
def get_dict(exclude: set = None, include: set = None)
```

Returns a dictionary of the account data. Using the exclude and include arguments, you can filter the data

**Arguments**:

- `exclude` _set_ - A set of keys to exclude
- `include` _set_ - A set of keys to include

<a id="backtest_account.BackTestAccount.asdict"></a>

#### asdict

```python
def asdict()
```

Returns a dictionary of the account data

<a id="backtest_account.BackTestAccount.set_attrs"></a>

#### set\_attrs

```python
def set_attrs(**kwargs)
```

Se the attributes of the account data to the instance

