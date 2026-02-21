# bot

`aiomql.lib.bot` — Bot orchestrator for running trading strategies.

## Overview

The `Bot` class is the main entry point for running one or more trading strategies against
the MetaTrader 5 terminal. It manages the account connection lifecycle, strategy
initialisation, task queuing, and graceful shutdown via signal handlers.

Inherits from [`_Base`](../core/base.md).

## Classes

### `Bot`

> Orchestrates strategy execution and terminal connection.

| Attribute | Type | Description |
|-----------|------|-------------|
| `account` | `Account` | The trading account instance |
| `executor` | `Executor` | Strategy and task executor |
| `mt5` | `MetaTrader` | MetaTrader terminal interface |

#### Lifecycle

| Method | Description |
|--------|-------------|
| `initialize()` | Connects to MT5 and logs in, sets up the executor |
| `start()` | Starts the bot: initialises, adds strategies, and runs the executor |
| `stop()` | Gracefully stops the bot and shuts down the terminal |
| `execute()` | Main execution loop |

#### Strategy Management

| Method | Description |
|--------|-------------|
| `add_strategy(strategy)` | Registers a `Strategy` subclass for execution |
| `add_strategies(*strategies)` | Registers multiple strategies at once |

#### Signal Handling

| Method | Description |
|--------|-------------|
| `sigint_handler(sig, frame)` | Handles SIGINT for graceful shutdown |

## Synchronous API

A synchronous variant is available in `aiomql.lib.sync.bot`.
