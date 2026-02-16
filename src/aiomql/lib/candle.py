"""Candle and Candles classes for handling price bars (OHLC data).

This module provides classes for working with candlestick/bar data from
MetaTrader 5. Includes support for technical analysis via pandas_ta,
charting with mplfinance, and various data manipulation operations.

Example:
    Working with candles::

        candles = await symbol.copy_rates_from_pos(timeframe=TimeFrame.H1, count=100)
        sma = candles.ta.sma(20)
        candles.plot(type='candle', volume=True)
"""

from datetime import datetime
from typing import Type, Self, Iterable, Protocol, runtime_checkable, Optional
from logging import getLogger

import pandas as pd
import mplfinance as mpf
from pandas import DataFrame, Series, DatetimeIndex, Timestamp

from ..ta_libs import pandas_ta_classic as ta
from ..core.constants import TimeFrame
from ..core.config import Config

logger = getLogger(__name__)


@runtime_checkable
class CandleProtocol(Protocol):
    """Protocol defining the minimal interface for Candle classes.

    Any class used as a `candle_class` argument in the Candles container
    must implement this protocol. This ensures type safety and provides
    a clear contract for custom candle implementations.

    Only the four core OHLC attributes are required. Custom candle classes
    can optionally inherit from CandleBase to get common methods like
    is_bullish(), is_bearish(), and wick/body calculations for free.

    Attributes:
        open: Opening price of the period.
        high: Highest price of the period.
        low: Lowest price of the period.
        close: Closing price of the period.
        

    Example:
        Creating a minimal custom candle class::

            class MyCandle:
                def __init__(self, **kwargs):
                    self.open = kwargs['open']
                    self.high = kwargs['high']
                    self.low = kwargs['low']
                    self.close = kwargs['close']

        Creating a custom candle with helper methods::

            class MyCandle(CandleBase):
                def __init__(self, **kwargs):
                    self.open = kwargs['open']
                    self.high = kwargs['high']
                    self.low = kwargs['low']
                    self.close = kwargs['close']
                    # Now has access to is_bullish(), is_bearish(), etc.
    """

    open: float
    high: float
    low: float
    close: float

    def __init__(self, **kwargs) -> None:
        """Initialize the candle with keyword arguments.

        Args:
            **kwargs: Must include 'open', 'high', 'low', 'close'.
        """
        ...


class CandleBase:
    """Base class providing common candle analysis methods.

    This class provides methods that only depend on the four core OHLC
    (Open, High, Low, Close) attributes. Custom candle classes can inherit
    from this class to get these methods for free.

    Attributes:
        open: Opening price of the period.
        high: Highest price of the period.
        low: Lowest price of the period.
        close: Closing price of the period.
        time: Period start time as Unix timestamp. Optional.
        index: Pandas Timestamp index. Optional.
        Index: Integer position index. Optional.

    Example:
        Creating a custom candle class with base methods::

            class MyCandle(CandleBase):
                def __init__(self, open, high, low, close):
                    self.open = open
                    self.high = high
                    self.low = low
                    self.close = close

            candle = MyCandle(open=100, high=110, low=95, close=105)
            print(candle.is_bullish())  # True
            print(candle.candle_body)   # 5.0
    """
    open: float
    high: float
    low: float
    close: float
    time: Optional[float] = None
    index: Optional[Timestamp] = None
    Index: Optional[int] = None

    def __repr__(self) -> str:
        """Return a string representation of the candle.

        Returns:
            str: String showing class name and OHLC values.
        """
        return (
            "%(class)s(open=%(open)s, high=%(high)s, low=%(low)s, close=%(close)s)"
            % {
                "class": self.__class__.__name__,
                "open": self.open,
                "high": self.high,
                "low": self.low,
                "close": self.close,
            }
        )

    @staticmethod
    def _comparison_key(candle) -> tuple[float, float]:
        """Return a tuple used for comparison operations.

        The comparison key consists of (candle_body, candle_range) which allows
        candles to be compared and sorted based on their body size and range.

        Args:
            candle: Any object implementing CandleProtocol (has open, high, low, close
                attributes) or a dict-like object with 'open', 'high', 'low', 'close' keys.

        Returns:
            tuple[float, float]: (candle_body, candle_range)
        """
        # Support both attribute access and dict-like access
        try:
            open_ = candle.open
            high = candle.high
            low = candle.low
            close = candle.close
        except AttributeError:
            open_ = candle['open']
            high = candle['high']
            low = candle['low']
            close = candle['close']
        return (abs(close - open_), high - low)

    def __eq__(self, other: "CandleProtocol") -> bool:
        """Check equality based on candle body and range.

        Two candles are equal if they have the same body size and range.

        Args:
            other: Any object implementing CandleProtocol.

        Returns:
            bool: True if candles have equal body and range.
        """
        return self._comparison_key(self) == self._comparison_key(other)

    def __ne__(self, other: "CandleProtocol") -> bool:
        """Check inequality based on candle body and range.

        Args:
            other: Any object implementing CandleProtocol.

        Returns:
            bool: True if candles have different body or range.
        """
        return self._comparison_key(self) != self._comparison_key(other)

    def __lt__(self, other: "CandleProtocol") -> bool:
        """Check if this candle is less than another based on body and range.

        Comparison is done lexicographically: first by body size, then by range.

        Args:
            other: Any object implementing CandleProtocol.

        Returns:
            bool: True if this candle is smaller.
        """
        return self._comparison_key(self) < self._comparison_key(other)

    def __le__(self, other: "CandleProtocol") -> bool:
        """Check if this candle is less than or equal to another.

        Args:
            other: Any object implementing CandleProtocol.

        Returns:
            bool: True if this candle is smaller or equal.
        """
        return self._comparison_key(self) <= self._comparison_key(other)

    def __gt__(self, other: "CandleProtocol") -> bool:
        """Check if this candle is greater than another based on body and range.

        Comparison is done lexicographically: first by body size, then by range.

        Args:
            other: Any object implementing CandleProtocol.

        Returns:
            bool: True if this candle is larger.
        """
        return self._comparison_key(self) > self._comparison_key(other)

    def __ge__(self, other: "CandleProtocol") -> bool:
        """Check if this candle is greater than or equal to another.

        Args:
            other: Any object implementing CandleProtocol.

        Returns:
            bool: True if this candle is larger or equal.
        """
        return self._comparison_key(self) >= self._comparison_key(other)

    def __hash__(self) -> int:
        """Return hash based on comparison key.

        Returns:
            int: Hash value based on (candle_body, candle_range).
        """
        return hash((self.open, self.high, self.low, self.close))

    def __getitem__(self, item: str):
        """Get an attribute value by key.

        Args:
            item: The attribute name to retrieve.

        Returns:
            The value of the requested attribute.

        Raises:
            KeyError: If the attribute does not exist.
        """
        return self.__dict__[item]

    def __setitem__(self, key: str, value) -> None:
        """Set an attribute value by key.

        Args:
            key: The attribute name to set.
            value: The value to assign to the attribute.
        """
        self.__dict__[key] = value

    def __iter__(self):
        """Iterate over attribute key-value pairs.

        Yields:
            tuple: (key, value) pairs for each instance attribute.
        """
        return iter(self.__dict__.items())

    def keys(self):
        """Return the attribute names of the candle.

        Returns:
            dict_keys: A view of the attribute names.
        """
        return self.__dict__.keys()

    def values(self):
        """Return the attribute values of the candle.

        Returns:
            dict_values: A view of the attribute values.
        """
        return self.__dict__.values()

    def set_attributes(self, **kwargs) -> None:
        """Set multiple attributes from keyword arguments.

        Args:
            **kwargs: Attribute names and values to set.
        """
        [setattr(self, i, j) for i, j in kwargs.items()]

    def dict(self, *, exclude: set = None, include: set = None) -> dict:
        """Return instance attributes as a dictionary.

        Args:
            exclude: Set of attribute names to exclude. Defaults to None.
            include: Set of attribute names to include. Defaults to None.

        Returns:
            dict: Dictionary of instance attributes.

        Note:
            If both include and exclude are provided, include takes precedence.
        """
        exclude = exclude or set()
        include = include or set()
        keys = include or set(self.__dict__.keys()).difference(exclude)
        return {k: v for k, v in self if k in keys}

    def to_series(self) -> Series:
        """Convert the candle to a pandas Series.

        Returns:
            Series: Pandas Series with candle attributes, excluding Index and index.
        """
        return Series(self.dict(exclude={"Index", "index"}))

    def is_bullish(self) -> bool:
        """Check if the candle is bullish (close >= open).

        Returns:
            bool: True if close >= open, False otherwise.
        """
        return self.close >= self.open

    def is_bearish(self) -> bool:
        """Check if the candle is bearish (close < open).

        Returns:
            bool: True if close < open, False otherwise.
        """
        return self.close < self.open

    @property
    def upper_wick(self) -> float:
        """Calculate the upper wick length.

        Returns:
            float: The distance from the high to max(open, close).
        """
        return self.high - max(self.open, self.close)

    @property
    def lower_wick(self) -> float:
        """Calculate the lower wick length.

        Returns:
            float: The distance from min(open, close) to the low.
        """
        return min(self.open, self.close) - self.low

    @property
    def candle_range(self) -> float:
        """Calculate the total range of the candle.

        Returns:
            float: The distance from high to low.
        """
        return self.high - self.low

    @property
    def candle_body(self) -> float:
        """Calculate the body size of the candle.

        Returns:
            float: The absolute distance between open and close.
        """
        return abs(self.close - self.open)

    @property
    def upper_wick_percentage(self) -> float:
        """Calculate the upper wick as a percentage of candle range.

        Returns:
            float: Upper wick percentage (0-100).
        """
        return self.upper_wick / self.candle_range * 100

    @property
    def lower_wick_percentage(self) -> float:
        """Calculate the lower wick as a percentage of candle range.

        Returns:
            float: Lower wick percentage (0-100).
        """
        return self.lower_wick / self.candle_range * 100

    @property
    def candle_body_percentage(self) -> float:
        """Calculate the body as a percentage of candle range.

        Returns:
            float: Body percentage (0-100).
        """
        return self.candle_body / self.candle_range * 100


class Candle(CandleBase):
    """MetaTrader 5 candle representation analogous to Japanese Candlesticks.

    This class extends CandleBase with additional attributes and methods specific
    to MetaTrader 5 candle data. You can subclass this class for added customization.

    Attributes:
        time: Period start time as Unix timestamp.
        open: Open price.
        high: Highest price of the period.
        low: Lowest price of the period.
        close: Close price.
        volume: Volume (uses real_volume or tick_volume).
        tick_volume: Tick volume.
        real_volume: Trade volume.
        spread: Spread value.
        index: Pandas Timestamp index.
        Index: Integer position for iloc-based indexing.
    """
    time: float
    open: float
    high: float
    low: float
    close: float
    volume: float
    real_volume: float
    spread: float
    tick_volume: float
    index: Timestamp
    Index: int

    def __init__(self, **kwargs):
        """Create a Candle object from keyword arguments.

        Args:
            **kwargs: Candle attributes. Must include 'open', 'high', 'low', 'close'.
                Optional: 'time', 'index', 'Index', 'volume', 'tick_volume',
                'real_volume', 'spread'.

        Raises:
            ValueError: If open, high, low, or close are not provided.
        """
        kwargs = {k.lower() if k != "Index" else k: v for k, v in kwargs.items() }
        if not all(i in kwargs for i in ["open", "high", "low", "close"]):
            raise ValueError("Candle must be instantiated with open, high, low and close prices")
        self.time = kwargs.pop("time", Timestamp.now().timestamp())
        self.Index = kwargs.pop("Index", 0)
        self.index = kwargs.pop("index", Timestamp(self.time, unit="s", tz=datetime.now().astimezone().tzinfo))
        self.real_volume = kwargs.pop("real_volume", 0)
        self.spread = kwargs.pop("spread", 0)
        self.tick_volume = kwargs.pop("tick_volume", 0)
        self.volume = kwargs.pop("volume", self.real_volume or self.tick_volume)
        self.set_attributes(**kwargs)

    def __repr__(self) -> str:
        """Return a string representation of the candle.

        Returns:
            str: String showing class name and all candle attributes.
        """
        return (
            "%(class)s(Index=%(Index)s, time=%(time)s, open=%(open)s, high=%(high)s, low=%(low)s, close=%(close)s, index=%(index)s)"
            % {
                "class": self.__class__.__name__,
                "open": self.open,
                "high": self.high,
                "low": self.low,
                "close": self.close,
                "time": self.time,
                "index": self.index.isoformat(),
                "Index": self.Index,
            }
        )

    def __hash__(self):
        """Return hash based on time and comparison key.

        Returns:
            int: Hash value based on (time, candle_body, candle_range).
        """
        return hash((self.time, self.open, self.high, self.low, self.close))


class Candles:
    """Iterable container of Candle objects in chronological order.

    Provides a DataFrame-backed container for candle data with support for
    technical analysis via pandas_ta, charting with mplfinance, and various
    data manipulation operations.

    Attributes:
        index: DatetimeIndex of the underlying DataFrame.
        Index: Series of integer position indices.
        time: Series of candle timestamps.
        open: Series of opening prices.
        high: Series of high prices.
        low: Series of low prices.
        close: Series of closing prices.
        volume: Series of volume values.
        tick_volume: Series of tick volume values.
        real_volume: Series of real volume values.
        spread: Series of spread values.
        timeframe: Detected TimeFrame of the candle data.
        Candle: The candle class used for iteration.
        data: The underlying pandas DataFrame.

    Note:
        The candle class can be customized by passing a custom class as the
        candle_class argument or by subclassing and setting the Candle attribute.
    """
    index: DatetimeIndex
    Index: Series
    time: Series
    open: Series
    high: Series
    low: Series
    close: Series
    volume: Series
    tick_volume: Series
    real_volume: Series
    spread: Series
    Candle: Type[CandleProtocol]
    timeframe: TimeFrame
    _data: DataFrame

    def __init__(self, *, data: DataFrame | Self | Iterable, flip=False, candle_class: Type[Candle] = None):
        """Initialize a Candles container.

        Args:
            data: Source data as DataFrame, Candles object, or iterable.
            flip: If True, reverse chronological order (most recent first).
                Defaults to False.
            candle_class: Custom candle class implementing CandleProtocol.
                Defaults to Candle.

        Raises:
            ValueError: If data cannot be converted to DataFrame.
        """
        if isinstance(data, DataFrame):
            data = data
        elif isinstance(data, type(self)):
            data = DataFrame(data.data)
        elif isinstance(data, Iterable):
            data = DataFrame(data)
        else:
            raise ValueError(f"Cannot create DataFrame from object of {type(data)}")

        self._data = data.loc[::-1] if flip else data
        if 'time' in self._data.columns:
            dtype = pd.DatetimeTZDtype(unit='s', tz=datetime.now().astimezone().tzinfo)
            self._data.index = pd.DatetimeIndex(self._data.time, dtype=dtype)

        self.Candle = candle_class or Candle
        self.config = Config()

    def __repr__(self) -> str:
        """Return string representation of the underlying DataFrame."""
        return repr(self._data)

    def __len__(self) -> int:
        """Return the number of candles in the container."""
        return len(self._data.index)

    def __contains__(self, item: Candle) -> bool:
        """Check if a candle exists in the container by time.

        Args:
            item: Candle object to check.

        Returns:
            bool: True if candle with matching time exists.
        """
        return item.time == self[item.Index].time

    def __getitem__(self, index: slice | int | str) -> Self | Series | Candle:
        """Get candle(s) by index, slice, or column name.

        Args:
            index: Integer index, slice, or column name string.

        Returns:
            Candle for int index, Candles for slice, Series for column name.

        Raises:
            TypeError: If index is not int, slice, or str.
        """
        if isinstance(index, slice):
            cls = self.__class__
            data = self._data.iloc[index]
            return cls(data=data)

        if isinstance(index, str):
            if index == "index":
                return self._data.index
            if index == "Index":
                return Series(range(len(self._data)))
            return self._data[index]

        if isinstance(index, int):
            candle = self._data.iloc[index]
            Index = index if index >= 0 else len(self) + index
            _index = self._data.index[index]
            return self.Candle(**candle, Index=Index, index=_index)
        raise TypeError(f"Expected int, slice or str got {type(index)}")

    def __setitem__(self, index: str, value: Series) -> None:
        """Set a column value by name.

        Args:
            index: Column name.
            value: Series to assign to the column.

        Raises:
            TypeError: If value is not a Series.
        """
        if isinstance(value, Series):
            self._data[index] = value
            return
        raise TypeError(f"Expected Series got {type(value)}")

    def __getattr__(self, item: str):
        """Get column or index by attribute name.

        Args:
            item: Attribute name (column name, 'index', or 'Index').

        Returns:
            Series or DatetimeIndex for the requested attribute.

        Raises:
            AttributeError: If attribute does not exist.
        """
        if item in self._data.columns:
            return self._data[item]

        if item == "index":
            return self._data.index

        if item == "Index":
            return Series(range(len(self._data)))
        raise AttributeError(f"Attribute {item} not defined on class {self.__class__.__name__}")

    def __reversed__(self):
        """Iterate over candles in reverse chronological order.

        Yields:
            Candle: Candle objects from newest to oldest.
        """
        for index, row in enumerate(iter(self._data[::-1].iloc)):
            row = row.to_dict()
            index = len(self._data) - index - 1
            row["Index"] = index
            row["index"] = self._data.index[index]
            yield self.Candle(**row)

    def __iter__(self):
        """Iterate over candles in chronological order.

        Yields:
            Candle: Candle objects from oldest to newest.
        """
        for index, row in enumerate(iter(self._data.iloc)):
            row = row.to_dict()
            row["Index"] = index
            row["index"] = self._data.index[index]
            yield self.Candle(**row)

    @property
    def timeframe(self) -> TimeFrame:
        """Detect the timeframe from consecutive candle timestamps.

        Returns:
            TimeFrame: The detected timeframe of the candle data.
        """
        tf = self.time.iloc[1] - self.time.iloc[0]
        return TimeFrame.get_timeframe(abs(tf))

    @property
    def columns(self):
        """Return the column names of the underlying DataFrame.

        Returns:
            Index: Column names.
        """
        return self._data.columns

    @property
    def ta(self):
        """Access pandas_ta for technical analysis on the data.

        Returns:
            pandas_ta accessor for the underlying DataFrame.
        """
        return self._data.ta

    @property
    def ta_lib(self):
        """Access the ta library directly.

        Returns:
            The pandas_ta module (not data-dependent).
        """
        return ta

    @property
    def data(self) -> DataFrame:
        """Return the underlying DataFrame.

        Returns:
            DataFrame: The candle data.
        """
        return self._data

    def rename(self, inplace: bool = True, **kwargs) -> Self:
        """Rename columns of the candles DataFrame.

        Args:
            inplace: If True, modify in place. If False, return new instance.
                Defaults to True.
            **kwargs: Column name mappings (old_name=new_name).

        Returns:
            Self: This instance if inplace, otherwise new Candles instance.
        """
        res = self._data.rename(columns=kwargs, inplace=inplace)
        return self if inplace else self.__class__(data=res)

    def __iadd__(self, other: Self) -> Self:
        """Merge another Candles object in place.

        Args:
            other: Candles object to merge.

        Returns:
            Self: This instance with merged data.
        """
        data_copy = self._data.copy()
        other = other._data
        for index, row in zip(other.index, iter(other.iloc)):
            data_copy.loc[index] = row
        self._data = data_copy.sort_index()
        return self

    def __add__(self, other: Self) -> Self:
        """Merge two Candles objects into a new instance.

        Args:
            other: Candles object to merge.

        Returns:
            Self: New Candles instance with merged data.
        """
        data = self._data.copy()
        for index, row in zip(other._data.index, iter(other._data.iloc)):
            data.loc[index] = row
        return self.__class__(data=data.sort_index())

    def add(self, obj: DataFrame | Series | Candle) -> Self:
        """Add new row(s) to the container.

        Args:
            obj: Data to add as DataFrame, Series, or Candle.

        Returns:
            Self: This instance with added data.

        Raises:
            TypeError: If obj is not DataFrame, Series, or Candle.
        """
        if isinstance(obj, Series):
            index = Timestamp(obj.time, unit="s", tz=datetime.now().astimezone().tzinfo)
            self._data.loc[index] = obj
            self._data = self._data.sort_index()
            return self
        elif isinstance(obj, DataFrame):
            data = self._data.copy()
            for index, row in zip(obj.index, iter(obj.iloc)):
                index = index if isinstance(index, Timestamp) else Timestamp(row.time, unit="s", tz=datetime.now().astimezone().tzinfo)
                data.loc[index] = row
            self._data = data.sort_index()
            return self
        elif isinstance(obj, Candle):
            self._data.loc[obj.index] = obj.to_series()
            self._data = self._data.sort_index()
            return self
        else:
            raise TypeError("Expected Series, DataFrame or Candle, got {}".format(type(obj)))

    def plot(self, subplots: dict = None, span: int = None, filename="", **kwargs):
        """Create a candlestick chart of the candle data.

        Args:
            subplots: Subplots to be added to the main plot. Defaults to None.
            span: Last 'n' candles to be used for the plot. Defaults to None (all candles).
            filename: Filename to save the plot. Defaults to empty string.
            **kwargs: Additional keyword arguments passed to mplfinance.plot().
        """
        type_ = kwargs.pop("type", "candle")
        subplots = subplots or []
        span = 0 if span is None else span
        data = self._data[-span:]
        if filename and not kwargs.get("savefig"):
            kwargs["savefig"] = self.config.plots_dir / filename

        mpf.plot(data, type=type_, addplot=subplots, **kwargs)

    def make_subplot(self, *, column: str | list[str], span: int = None, **kwargs) -> dict:
        """Create a subplot for use with the plot method.

        Args:
            column: Column name(s) for the subplot data.
            span: Last 'n' candles to be used for the subplot. Defaults to None (all candles).
            **kwargs: Additional keyword arguments passed to mplfinance.make_addplot().

        Returns:
            dict: Subplot configuration for mplfinance.
        """
        column = column if isinstance(column, list) else [column]
        span = 0 if span is None else span
        data = self._data[-span:]
        data = data[column]
        return mpf.make_addplot(data, **kwargs)
