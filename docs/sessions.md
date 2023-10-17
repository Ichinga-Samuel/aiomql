## <a id="sessions"></a> Sessions and Session

Sessions allow you to run code at specific times of the day.

```python
class Session()
```
A session is a time period between two datetime.time objects specified in utc.

### Attributes:
|Name| Type           | Description                                                            | Default |
|---|----------------|------------------------------------------------------------------------|----|
|**start**| **datetime.time** | The start time of the session.                                         | None |
|**end**| **datetime.time** | The end time of the session.                                           | None |
|**on_start**| **Literal['close_all', 'close_win', 'close_loss', 'custom_start']**  | The action to take when the session starts. Default is None.           | None |
|**on_end**| **Literal['close_all', 'close_win', 'close_loss', 'custom_end']**           | The action to take when the session ends. Default is None.             | None |
|**custom_start**| **Callable**   | A custom function to call when the session starts. Default is None.    | None |
|**custom_end**| **Callable**   | A custom function to call when the session ends. Default is None.      | None |
|**name**| **str**        | The name of the session. Default is a combination of start and finish. |    |
|**seconds**| **set[int]**   | The set of seconds in the session.                                     | None |

### Methods:
|Name|Description|
|---|---|
|**begin**|Call the action specified in on_start or custom_start.|
|**close**|Call the action specified in on_end or custom_end.|
|**action**|Used by begin and close to call the action specified.|
|**until**|Get the seconds until the session starts from the current time.|

### \_\_init\_\_

```python
def __init__(*,
             start: int | time,
             end: int | time,
             on_start: Literal['close_all', 'close_win', 'close_loss',
                               'custom_start'] = None,
             on_end: Literal['close_all', 'close_win', 'close_loss',
                             'custom_end'] = None,
             custom_start: Callable = None,
             custom_end: Callable = None)
```
Create a session.
#### Arguments:
|Name| Type                    | Description  | Default           |
|---|-------------------------|--------------|-------------------|
|**start**| **int** \|   **datetime.time** | The start time of the session in UTC. | None |
|**end**| **int** \|   **datetime.time** | The end time of the session in UTC. | None |
|**on_start**| **Literal['close_all', 'close_win', 'close_loss', 'custom_start']** | The action to take when the session starts. Default is None. | None | 
|**on_end**| **Literal['close_all', 'close_win', 'close_loss', 'custom_end']** | The action to take when the session ends. Default is None. | None |
|**custom_start**| **Callable** | A custom function to call when the session starts. Default is None. | None |
|**custom_end**| **Callable** | A custom function to call when the session ends. Default is None. | None |
|**name**| **str** | The name of the session. Default is None. | None |

### begin
```python
async def begin()
```
Call the action specified in on_start or custom_start.

### close
```python
async def close()
```
Call the action specified in on_end or custom_end.
### action
```python
async def action(action)
```
Used by begin and close to call the action specified.

#### Arguments:
|Name| Type                    | Description  | Default           |
|---|-------------------------|--------------|-------------------|
|**action**| **Literal['close_all', 'close_win', 'close_loss', 'custom_start', 'custom_end']** | The action to take. | None |

### delta
```python
@staticmethod
def delta(obj: time)
```
Get the timedelta of a datetime.time object.

#### Arguments:
|Name| Type                    | Description  | Default           |
|---|-------------------------|--------------|-------------------|
|**obj**| **datetime.time** | A datetime.time object. | None |

#### Returns:
|Type|Description|
|---|---|
|**timedelta**|A timedelta object.|

### until
```python
def until()
```
Get the seconds until the session starts from the current time.
#### Returns:
|Type|Description|
|---|---|
|**int**|The seconds until the session starts.|


## Sessions

```python
class Sessions()
```
Sessions allow you to run code at specific times of the day. It is a collection of Session objects.
Sessions are sorted by start time. The sessions object is an asynchronous context manager.
### Attributes:
|Name|Type|Description|Default|
|---|---|---|---|
|**sessions**|**list[Session]**|A list of Session objects.|[]|
|**current_session**|**Session**|The current session.|None|

### Methods:
|Name|Description|
|---|---|
|**add**|Add a Session object to the sessions list.|
|**remove**|Remove a Session object from the sessions list.|
|**find**|Find a session that contains a datetime.time object.|
|**find_next**|Find the next session that contains a datetime.time object.|
|**check**|Check if the current session has started and if not, wait until it starts.|

#### \_\_init\_\_
```python
def __init__(*sessions)
```
Create a Sessions object.
#### Arguments:
|Name| Type               | Description                 | Default           |
|---|--------------------|-----------------------------|-------------------|
|**sessions**| **tuple[Session]** | A tuple of Session objects. | None |

### find
```python
def find(obj: time) -> Session | None
```
Find a session that contains a datetime.time object.
#### Arguments:
|Name| Type                    | Description  | Default           |
|---|-------------------------|--------------|-------------------|
|**obj**| **datetime.time** | A datetime.time object. | None |

#### Returns:
|Type|Description|
|---|---|
|**Session**|A Session object or None if not found.|

### find\_next
```python
def find_next(obj: time) -> Session
```
Find the next session that contains a datetime.time object.
#### Arguments:
|Name| Type                    | Description  | Default           |
|---|-------------------------|--------------|-------------------|
|**obj**| **datetime.time** | A datetime.time object. | None |
#### Returns:
|Type|Description|
|---|---|
|**Session**|A Session object.|


### check
```python
async def check()
```
Check if the current session has started and if not, wait until it starts.
