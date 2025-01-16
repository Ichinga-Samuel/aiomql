# Changelog

## [4.0.7](https://github.com/Ichinga-Samuel/aiomql/releases/tag/v4.0.7) - 2025-01-16

### Changed
- Candles underlying DataFrame is now indexed by datetime.
- Executor runs a strategy via the `run_strategy` method directly with `asyncio.run` without creating as a task.
- `Strategy` class now has a initialize method that is called before the strategy is run.

### Added
- `__add__` and `__iadd__` dunder methods for addition and inplace addition of dataframes or series objects to the Candles object.
- `add` method for adding dataframes or series objects to the Candles object.

### Fixed
- Candles timeframe attribute returns the correct TimeFrame object.
