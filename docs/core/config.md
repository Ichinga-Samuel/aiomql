# Config

## Table of Contents
- [Config](#config.config)
- [account_info](#config.account_info)
- [backtest_engine](#config.backtest_engine)
- [set_attributes](#config.set_attributes)
- [load_config](#config.load_config)
 

<a id="config.config"></a>
```python
class Config
```
The global config object. It is a singleton class for handling configuration settings for the aiomql package.
A single instance of this class is created and used per bot instance.

#### Attributes:
| Name                           | Type                          | Description                                                             |
|--------------------------------|-------------------------------|-------------------------------------------------------------------------|
| `login`                        | `int`                         | The account login number                                                |
| `trade_record_mode`            | `Literal["csv", "json"]`      | The mode for recording trades                                           |
| `password`                     | `str`                         | The account password                                                    |
| `server`                       | `str`                         | The account server                                                      |
| `path`                         | `str \| Path`                 | The path to the terminal                                                |
| `timeout`                      | `int`                         | The timeout argument for the terminal                                   |
| `filename`                     | `str`                         | The filename of the config file                                         |
| `state`                        | `dict`                        | The state of the configuration                                          |
| `root`                         | `Path`                        | The root directory of the project                                       |
| `record_trades`                | `bool`                        | To record trades or not. Default is True                                |
| `records_dir`                  | `Path`                        | The directory to store trade records, relative to the root directory    |
| `records_dir_name`             | `str`                         | The name of the trade records directory                                 |
| `backtest_dir`                 | `Path`                        | The directory to store backtest results, relative to the root directory |
| `backtest_dir_name`            | `str`                         | The name of the backtest directory                                      |
| `task_queue`                   | `TaskQueue`                   | The TaskQueue object for handling background tasks                      |
| `_backtest_engine`             | `BackTestEngine`              | The backtest engine object                                              |
| `bot`                          | `Bot`                         | The bot object                                                          |
| `_instance`                    | `Self`                        | The instance of the Config class                                        |
| `mode`                         | `Literal["backtest", "live"]` | The trading mode, either backtest or live, default is live              |
| `use_terminal_for_backtesting` | `bool`                        | Use the terminal for backtesting, default is True                       |
| `shutdown`                     | `bool`                        | A signal to shut down the terminal, default is False                    |
| `force_shutdown`               | `bool`                        | A signal to force shut down the terminal, default is False              |

#### Notes:
By default, the config class looks for a file named aiomql.json. This can be changed by setting the filename
attribute to the desired file name. The root directory of the project can be set by passing the root argument
to the load_config method or during object instantiation. If not provided it is assumed to be the current working
directory. All directories and files are assumed to be relative to the root directory except when an absolute path
is provided, this includes the config file, the records_dir and the backtest_dir attributes.
The root directory is used to locate the config file and to set the records_dir and backtest_dir attributes.


<a id="config.account_info"></a>
### account_info
```python
def account_info() -> dict['login', 'password', 'server']
```
Returns Account login details as found in the config object if available

#### Returns:
| Type                                  | Description                                           |
|---------------------------------------|-------------------------------------------------------|
| `dict['login', 'password', 'server']` | A dictionary with login, password, and server details |

<a id="config.backtest_engine"></a>
### backtest_engine
```python
@property
def backtest_engine(self)
```
Returns the backtest engine object.

#### Returns:
| Type            | Description            |
|-----------------|------------------------|
| `BackTestEngine` | The backtest engine object |


<a id="config.backtest_engine.setter"></a>
```python
@backtest_engine.setter
def backtest_engine(self, value: BackTestEngine)
```
Sets the backtest engine object.

#### Parameters:
| Name    | Type             | Description                |
|---------|------------------|----------------------------|
| `value` | `BackTestEngine` | The backtest engine object |

<a id="config.set_attributes"></a>
### set_attributes
```python
def set_attributes(self, **kwargs)
```
Set attributes on the config object. The root folder attribute can't be set here.

<a id="config.load_config"></a>
### load_config
```python
def load_config(*, file: str | Path = None, filename: str = None, root: str | Path = None, **kwargs) -> Config
```
Load configuration settings from a file and reset the config object.

#### Parameters:
| Name       | Type          | Description                                                                                        |
|------------|---------------|----------------------------------------------------------------------------------------------------|
| `file`     | `str \| Path` | The absolute path to the config file.                                                              |
| `filename` | `str`         | The name of the file to load if file path is not specified. If not provided `aiomql.json` is used. |
| `root`     | `str`         | The root directory of the project.                                                                 |
| `**kwargs` | `dict`        | Additional keyword arguments to be set on the config object.                                       |
