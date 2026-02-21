# exceptions

`aiomql.core.exceptions` — Custom exception hierarchy for the aiomql package.

## Overview

Defines domain-specific exceptions used throughout the library to signal
trading and connection errors.

## Exceptions

| Exception | Base | Description |
|-----------|------|-------------|
| `LoginError` | `Exception` | Raised when a login attempt fails |
| `VolumeError` | `Exception` | Raised when a volume is invalid or out of range for a symbol |
| `SymbolError` | `Exception` | Raised when a required symbol is missing or not in Market Watch |
| `OrderError` | `Exception` | Raised when an error occurs while working with the `Order` class |
| `StopTrading` | `Exception` | Raised to signal that trading should stop |
| `InvalidRequest` | `Exception` | Raised when a market query fails |
