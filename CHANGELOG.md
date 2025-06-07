# Changelog

## [4.0.13](https://github.com/Ichinga-Samuel/aiomql/releases/tag/v4.0.13) - 2025-03-24

### Fixed

- Fixed Candles inplace addition and addition to be only between candles objects
- Index of Candles object dataframe is now a timezone-aware DateTimeIndex
- Add method can accept addition of either a Series, DataFrame, or Candle, object

### Added 

- A to_series method to both Tick and Candle Classes
- Index attribute is now strictly for integer-based indexing
- index attribute maps to the underlying label-based indexing of the dataframe

## [4.0.12](https://github.com/Ichinga-Samuel/aiomql/releases/tag/v4.0.12) - 2025-03-24

### Fixed

- Use correct error handling decorator for modify_stops in backtester

## [4.0.10](https://github.com/Ichinga-Samuel/aiomql/releases/tag/v4.0.10) - 2025-01-24

### Changed

- Removed backoff decorator from send method of `Order` class

## [4.0.9](https://github.com/Ichinga-Samuel/aiomql/releases/tag/v4.0.9) - 2025-01-23

### Fixed

- Fixed `__add__` to return a new Candles object

### Changed

- Removed tasks attribute from executor class

### Added

- Added `initialize_sync` method for synchronous initialization of a symbol


## [4.0.8](https://github.com/Ichinga-Samuel/aiomql/releases/tag/v4.0.8) - 2025-01-21

### Fixed

- Fixed `__add__` to return a new Candles object

### Changed

- Index attribute of a Candle now based on iloc of the Candles DataFrame

## [4.0.7](https://github.com/Ichinga-Samuel/aiomql/releases/tag/v4.0.7) - 2025-01-16

### Changed
- 
- Candles underlying DataFrame is now indexed by datetime.
- Executor runs a strategy via the `run_strategy` method directly with `asyncio.run` without creating as a task.
- `Strategy` class now has a initialize method that is called before the strategy is run.

### Added
- 
- `__add__` and `__iadd__` dunder methods for addition and inplace addition of dataframes or series objects to the Candles object.
- `add` method for adding dataframes or series objects to the Candles object.

### Fixed
- 
- Candles timeframe attribute returns the correct TimeFrame object.
