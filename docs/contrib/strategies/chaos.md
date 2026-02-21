# chaos

`aiomql.contrib.strategies.chaos` — Random buy/sell demo strategy.

## Overview

The `Chaos` strategy randomly buys or sells on every tick, serving as a minimal
working example of a `Strategy` subclass. Useful for testing the trading pipeline.

## Classes

### `Chaos`

> Demo strategy that trades randomly.

Inherits from [`Strategy`](../../lib/strategy.md).

#### `trade()`

Generates a random `OrderType` (BUY or SELL) and places a market order via the
configured trader.
