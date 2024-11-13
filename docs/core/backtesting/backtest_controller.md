# Table of Contents

* [backtest\_controller](#backtest_controller)
  * [BackTestController](#backtest_controller.BackTestController)
    * [backtest\_engine](#backtest_controller.BackTestController.backtest_engine)
    * [add\_tasks](#backtest_controller.BackTestController.add_tasks)
    * [set\_parties](#backtest_controller.BackTestController.set_parties)
    * [parties](#backtest_controller.BackTestController.parties)
    * [control](#backtest_controller.BackTestController.control)
    * [stop\_backtesting](#backtest_controller.BackTestController.stop_backtesting)
    * [wait](#backtest_controller.BackTestController.wait)
    * [abort](#backtest_controller.BackTestController.abort)

<a id="backtest_controller"></a>

# backtest\_controller

<a id="backtest_controller.BackTestController"></a>

## BackTestController Objects

```python
class BackTestController()
```

The controller for the backtesting engine.
It also act's as a synchronizier for running multiple strategies (tasks) using a threading.Barrier primitive.
It handles the updating of open positions and close them when necessary.
It handles the iterator for the backtesting engine and handles it movement in time by moving it to the next time step.

**Attributes**:

- `_instance` _Self_ - The instance of the controller
- `config` _Config_ - The configuration for the backtesting engine
- `tasks` _list[Task]_ - The tasks that are being run
- `barrier` _Barrier_ - The barrier for synchronizing the tasks

<a id="backtest_controller.BackTestController.backtest_engine"></a>

#### backtest\_engine

```python
@property
def backtest_engine()
```

Returns the backtest engine

<a id="backtest_controller.BackTestController.add_tasks"></a>

#### add\_tasks

```python
def add_tasks(*tasks: Task)
```

Adds tasks to the tasks list

<a id="backtest_controller.BackTestController.set_parties"></a>

#### set\_parties

```python
def set_parties(*, parties: int)
```

Sets the number of parties for the barrier. The barrier will wait for the number of parties to reach the barrier.
This has to be done here as it can be impossible to know the eventual number of parties to set the barrier to during initialization.

**Arguments**:

- `parties` _int_ - The number of parties to set the barrier to

<a id="backtest_controller.BackTestController.parties"></a>

#### parties

```python
@property
def parties()
```

Returns the number of parties for the barrier

<a id="backtest_controller.BackTestController.control"></a>

#### control

```python
async def control()
```

The backtest controller. It controls the backtesting engine and the tasks that are being run.
It acts as a synchronizer for the tasks and the backtesting engine.

<a id="backtest_controller.BackTestController.stop_backtesting"></a>

#### stop\_backtesting

```python
def stop_backtesting()
```

Stop the backtester, and shutdown the executor

<a id="backtest_controller.BackTestController.wait"></a>

#### wait

```python
def wait()
```

Called by individual tasks to indicate completion of their cycle

<a id="backtest_controller.BackTestController.abort"></a>

#### abort

```python
def abort()
```

Aborts the barrier

