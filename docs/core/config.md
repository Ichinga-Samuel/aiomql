# Config

## Table of Contents
- [Config](#config.Config)
- [account\_info](#config.account_info)
- [load\_config](#config.load_config)
- [create\_records\_dir](#config.create_records_dir)
 

<a id="config.Config"></a>
```python
class Config
```
A class for handling configuration settings for the aiomql package. A single instance of this class is created and used
per bot instance.
### Class Attributes
| Name             | Type         | Description                                         | Default                                             |
|------------------|--------------|-----------------------------------------------------|-----------------------------------------------------|
| `record\_trades` | `bool`       | Whether to keep record of trades or not.            | True                                                |
| `filename`       | `str`        | Name of the config file                             | aiomql.json                                         |
| `records\_dir`   | `str\| Path` | Path to the directory where trade records are saved | Should be relative to the project root              |
| `login`          | `str`        | Trading account number                              |                                                     |
| `password`       | `str`        | Trading account password                            |                                                     |
| `server`         | `str`        | Broker server                                       |                                                     |
| `path`           | `str\|Path`  | Path to terminal file                               | Absolute                                            |
| `timeout`        | `int`        | Timeout for terminal connection                     |                                                     |
| `config_dir`     | `str`        | Directory where the config file is located          | Optional. Should be relative to the root directory  |
| `state`          | `dict`       | A global state object                               |                                                     |
| `task_queue`     | `Queue`      | A global queue for handling tasks                   |                                                     |
| `bot`            | `Bot`        | The bot instance                                    | Added to the config object after bot initialization |
| `root_dir`       | `str`        | Root directory of the project                       |                                                     |

#### Notes
By default, the config class looks for a file named aiomql.json.
You can change this by passing the filename keyword argument to the constructor.
By passing reload=True to the load_config method, you can reload and search again for the config file.

<a id="config.account_info"></a>
### account\_info
```python
def account_info() -> dict['login', 'password', 'server']
```
Returns Account login details as found in the config object if available
#### Returns
| Type   | Description                                           |
|--------|-------------------------------------------------------|
| `dict` | A dictionary with login, password, and server details |

<a id="config.load_config"></a>
### load\_config
```python
def load_config(self, *, file: str = None, reload: bool = True, filename: str = None, config_dir: str = '')
```
Load configuration settings from a file.
#### Parameters
| Name         | Type   | Description                                                                                                 |
|--------------|--------|-------------------------------------------------------------------------------------------------------------|
| `file`       | `str`  | The file to load the configuration settings from. If not provided, the default file is used.                |
| `reload`     | `bool` | Whether to reload the configuration settings or not.                                                        |
| `filename`   | `str`  | The name of the file to load the configuration settings from. If not provided, the default filename is used |                               
| `config_dir` | `str`  | The directory where the configuration file is located.  Default is the root directory                       |                               

<a id="config.create_records_dir"></a>
### create_records_dir
```python
def create_records_dir(self, *, records_dir: str | Path = 'records'):
```
Create a directory for saving trade records.
#### Parameters
| Name           | Type        | Description                                                       |
|----------------|-------------|-------------------------------------------------------------------|
| `records\_dir` | `str\|Path` | The directory where trade records are saved. Default is 'records' |
