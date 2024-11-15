# BackTestController

## Table of Contents
- [BackTestController](#backtest_controller.back_test_controller)
- [backtest_engine](#backtest_controller.backtest_engine)
- [add_tasks](#backtest_controller.add_tasks)
- [set_parties](#backtest_controller.set_parties)
- [parties](#backtest_controller.parties)
- [control](#backtest_controller.control)
- [stop_backtesting](#backtest_controller.stop_backtesting)
- [wait](#backtest_controller.wait)
- [abort](#backtest_controller.abort)


<a id="backtest_controller.back_test_controller"></a>
### BackTestController
```python
class BackTestController
```
The controller for the backtesting engine.
It also acts as a synchronizer for running multiple strategies (tasks) using a threading.Barrier primitive.
It handles the updating of open positions and close them when necessary.
It handles the iterator for the backtesting engine and handles it movement in time by moving it to the next time step.

#### Attributes:
| Name        | Type                 | Description                                  |
|-------------|----------------------|----------------------------------------------|
| `_instance` | `BackTestController` | The instance of the controller               |
| `config`    | `Config`             | The configuration for the backtesting engine |
| `tasks`     | `list[Task]`         | The tasks that are being run                 |
| `barrier`   | `Barrier`            | The barrier for synchronizing the tasks      |


<a id="backtest_controller.backtest_engine"></a>
#### backtest_engine
```python
@property
def backtest_engine()
```
Returns the backtest engine


<a id="backtest_controller.add_tasks"></a>
#### add_tasks
```python
def add_tasks(*tasks: Task)
```
Adds a task to the tasks list


<a id="backtest_controller.set_parties"></a>
#### set_parties
```python
def set_parties(*, parties: int)
```
Sets the number of parties for the barrier. The barrier will wait for the number of parties to reach the barrier.
This has to be done here as it can be impossible to know the eventual number of parties to set the barrier to during initialization.

#### Parameters:
| Name      | Type  | Description                                 |
|-----------|-------|---------------------------------------------|
| `parties` | `int` | The number of parties to set the barrier to |


<a id="backtest_controller.parties"></a>
#### parties
```python
@property
def parties()
```
Returns the number of parties for the barrier


<a id="backtest_controller.control"></a>
#### control
```python
async def control()
```
The backtest controller. It controls the backtesting engine and the tasks that are being run.
It acts as a synchronizer for the tasks and the backtesting engine.


<a id="backtest_controller.stop_backtesting"></a>
#### stop_backtesting
```python
def stop_backtesting()
```
Stop the backtester, and shutdown the executor


<a id="backtest_controller.wait"></a>
#### wait
```python
def wait()
```
Called by individual tasks to indicate completion of their cycle


<a id="backtest_controller.abort"></a>
#### abort
```python
def abort()
```
Aborts the barrier
