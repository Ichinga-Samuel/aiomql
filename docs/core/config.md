# Table of Contents

* [aiomql.core.config](#aiomql.core.config)
  * [Config](#aiomql.core.config.Config)
    * [account\_info](#aiomql.core.config.Config.account_info)

<a id="aiomql.core.config"></a>

# aiomql.core.config

<a id="aiomql.core.config.Config"></a>

## Config Objects

```python
class Config()
```

A class for handling configuration settings for the aiomql package.

**Arguments**:

- `**kwargs` - Configuration settings as keyword arguments.
  Variables set this way supersede those set in the config file.
  

**Attributes**:

- `record_trades` _bool_ - Whether to keep record of trades or not.
- `filename` _str_ - Name of the config file
- `records_dir` _str_ - Path to the directory where trade records are saved
- `win_percentage` _float_ - Percentage of achieved target profit in a trade to be considered a win
- `login` _int_ - Trading account number
- `password` _str_ - Trading account password
- `server` _str_ - Broker server
- `path` _str_ - Path to terminal file
- `timeout` _int_ - Timeout for terminal connection
  

**Notes**:

  By default, the config class looks for a file named aiomql.json.
  You can change this by passing the filename keyword argument to the constructor.
  By passing reload=True to the load_config method, you can reload and search again for the config file.

<a id="aiomql.core.config.Config.account_info"></a>

#### account\_info

```python
def account_info() -> dict['login', 'password', 'server']
```

Returns Account login details as found in the config object if available

**Returns**:

- `dict` - A dictionary of login details

