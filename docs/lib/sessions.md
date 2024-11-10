from aiomql import TradePositionfrom aiomql.lib.sessions import Duration

# Session and Sessions
Sessions allow you to run a strategy at specific times of the day.

## Table of Contents
- [Session](#session)
    - [\__init\__](#session.__init__)
    - [begin](#session.begin)
    - [close](#session.close)
    - [action](#session.action)
    - [in_session](#session.in_session)
    - [duration](#session.duration)
    - [close_positions](#session.close_positions)
    - [close_all](#session.close_all)
    - [close_win](#session.close_win)
    - [close_loss](#session.close_loss)
    - [close_until](#session.until)
- [Sessions](#sessions.sessions)
    - [\__init\__](#sessions.__init__)
    - [find](#sessions.find)
    - [find_next](#sessions.find_next)
    - [check](#sessions.check)
- [delta](#sessions_mod.delta)
- [backtest_sleep](#sessions_mod.backtest_sleep)
  

<a id="session.session"></a>
## Session
```python
class Session
```
A session is a time period between two `datetime.time` objects specified in utc.

#### Attributes:
| Name           | Type                                                              | Description                                                            | Default |
|----------------|-------------------------------------------------------------------|------------------------------------------------------------------------|---------|
| `start`        | `datetime.time`                                                   | The start time of the session.                                         | None    |
| `end`          | `datetime.time`                                                   | The end time of the session.                                           | None    |
| `on_start`     | `Literal['close_all', 'close_win', 'close_loss', 'custom_start']` | The action to take when the session starts. Default is None.           | None    |
| `on_end`       | `Literal['close_all', 'close_win', 'close_loss', 'custom_end']`   | The action to take when the session ends. Default is None.             | None    |
| `custom_start` | `Callable`                                                        | A custom function to call when the session starts. Default is None.    | None    |
| `custom_end`   | `Callable`                                                        | A custom function to call when the session ends. Default is None.      | None    |
| `name`         | `str`                                                             | The name of the session. Default is a combination of start and finish. |         |

#### Notes:
The `[close_all, close_win, close_loss]` will affect or open positions in the account irrespective of whether they were
opened during the session or not or even by a strategy using the session. This is because the session is not aware of the
positions opened by the strategy. This will be handled in a future release.

<a id="session.__init__"></a>
### \__init\__
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
Create a session
#### Parameters:
| Name           | Type                                                              | Description                                                         | Default |
|----------------|-------------------------------------------------------------------|---------------------------------------------------------------------|---------|
| `start`        | `int` \|   `datetime.time`                                        | The start time of the session in UTC.                               | None    |
| `end`          | `int` \|   `datetime.time`                                        | The end time of the session in UTC.                                 | None    |
| `on_start`     | `Literal['close_all', 'close_win', 'close_loss', 'custom_start']` | The action to take when the session starts. Default is None.        | None    | 
| `on_end`       | `Literal['close_all', 'close_win', 'close_loss', 'custom_end']`   | The action to take when the session ends. Default is None.          | None    |
| `custom_start` | `Callable`                                                        | A custom function to call when the session starts. Default is None. | None    |
| `custom_end`   | `Callable`                                                        | A custom function to call when the session ends. Default is None.   | None    |
| `name`         | `str`                                                             | The name of the session. Default is None.                           | None    |


<a id="session.begin"></a>
### begin
```python
async def begin()
```
Call the action specified in on_start or custom_start.


<a id="session.close"></a>
### close
```python
async def close()
```
Call the action specified in on_end or custom_end.


<a id="session.in_session"></a>
### in_session
```python
def in_session() -> bool
```
Check if the current time is within the current session.


<a id="session.duration"></a>
### duration
```python
def duration() -> Duration
```
Get the duration of the session in hours, minutes, and seconds.


<a id="session.close_positions"></a>
### close_positions
```python
async def close_positions(*, positions: tuple[TradePosition, ...])
```
Close positions in the sessions. This is used by the `close_all` action.

#### Parameters:
| Name        | Type                        | Description                           |
|-------------|-----------------------------|---------------------------------------|
| `positions` | `tuple[TradePosition, ...]` | A tuple of TradePosition objects.     |


<a id="session.close_all"></a>
### close_all
```python
async def close_all()
```
Close all open positions


<a id="session.close_win"></a>
### close_win
```python
async def close_win()
```
Close only winning positions


<a id="session.close_loss"></a>
### close_loss
```python
async def close_loss()
```
Close only losing positions


<a id="session.action"></a>
### action
```python
async def action(*, action: Literal["close_all", "close_win", "close_loss", "custom_start", "custom_end"]): pass
```
Used by begin and close to call the action specified.

#### Parameters:
| Name     | Type                                                                            | Description         |
|----------|---------------------------------------------------------------------------------|---------------------|
| `action` | `Literal['close_all', 'close_win', 'close_loss', 'custom_start', 'custom_end']` | The action to take. |


<a id="session.until"></a>
### until
```python
def until() -> int
```
Get the seconds until the session starts from the current time.


<a id="sessions.sessions"></a>
## Sessions
```python
class Sessions()
```
Sessions allow you to run code at specific times of the day. It is a collection of Session objects.
Sessions are sorted by start time. The sessions object is an asynchronous context manager.

### Attributes:
| Name              | Type            | Description                | Default |
|-------------------|-----------------|----------------------------|---------|
| `sessions`        | `list[Session]` | A list of Session objects. | []      |
| `current_session` | `Session`       | The current session.       | None    |


<a id="sessions.__init__"></a>
#### \__init\__
```python
def __init__(*sessions: Iterable[Session])
```
Create a Sessions object.
#### Parameters:
| Name       | Type                | Description                    |
|------------|---------------------|--------------------------------|
| `sessions` | `Iterable[Session]` | A iterable of Session objects. |


<a id="sessions.find"></a>
### find
```python
def find(*, moment: time = None) -> Session | None
```
Find a session that contains a datetime.time object.

#### Parameters:
| Name     | Type   | Description             | Default |
|----------|--------|-------------------------|---------|
| `moment` | `time` | A datetime.time object. | None    |

#### Returns:
| Type      | Description                            |
|-----------|----------------------------------------|
| `Session` | A Session object or None if not found. |


<a id="sessions.find_next"></a>
### find_next
```python
def find_next(*, moment: time = None) -> Session
```
Find the next session that contains a datetime.time object.
#### Parameters:
| Name     | Type   | Description             | Default |
|----------|--------|-------------------------|---------|
| `moment` | `time` | A datetime.time object. |         |

#### Returns:
| Type      | Description       |
|-----------|-------------------|
| `Session` | A Session object. |


<a id="sessions.check"></a>
### check
```python
async def check(): pass
```
Check if the current session has started and if not, wait until it starts.


<a id="sessions_mod.delta"></a>
### delta
```python
def delta(obj: time) -> timedelta: pass
```
Get the timedelta of a datetime.time object.

#### Parameters:
| Name  | Type            | Description             | Default |
|-------|-----------------|-------------------------|---------|
| `obj` | `datetime.time` | A datetime.time object. | None    |
#### Returns
| Type        | Description         |
|-------------|---------------------|
| `timedelta` | A timedelta object. |


<a id="sessions_mod.backtest_sleep"></a>
### backtest_sleep
```python
async def backtest_sleep(secs)
```
Sleep method for backtesting.
