"""Candle and Candles classes for handling bars from the MetaTrader 5 terminal."""

from datetime import datetime
from typing import Type, Self, Iterable
from logging import getLogger

import pandas as pd
import mplfinance as mpf
from pandas import DataFrame, Series, DatetimeIndex, Timestamp
import pandas_ta as ta
from ..core.constants import TimeFrame
from ..core.config import Config

logger = getLogger(__name__)


class Candle:
    """A customized class representing rates from the MetaTrader 5 terminal analogous to Japanese
    Candlesticks. You can subclass this class for added customization.

    Attributes:
        time (float): Period start time.
        open (float): Open price
        high (float): The highest price of the period
        low (float): The lowest price of the period
        close (float): Close price
        tick_volume (float): Tick volume
        real_volume (float): Trade volume
        spread (float): Spread
        index (Timestamp): Index of the object in the DataFrame, a timestamp
        Index (int): Custom attribute representing the position of the candle for integer-location based indexing
    """
    time: float
    open: float
    high: float
    low: float
    close: float
    real_volume: float
    spread: float
    tick_volume: float
    index: Timestamp
    Index: int

    def __init__(self, **kwargs):
        """Create a Candle object from keyword arguments. This class must always be instantiated with open, high, low
         and close prices.

        Keyword Args:
            **kwargs: Candle attributes and values as keyword arguments.
        """
        if not all(i in kwargs for i in ["open", "high", "low", "close"]):
            raise ValueError("Candle must be instantiated with open, high, low and close prices")
        self.time = kwargs.pop("time", Timestamp.now().timestamp())
        self.Index = kwargs.pop("Index", 0)
        self.index = kwargs.pop("index", Timestamp(self.time, unit="s", tz=datetime.now().astimezone().tzinfo))
        self.real_volume = kwargs.pop("real_volume", 0)
        self.spread = kwargs.pop("spread", 0)
        self.tick_volume = kwargs.pop("tick_volume", 0)
        self.set_attributes(**kwargs)

    def __repr__(self):
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

    def __eq__(self, other: Self):
        return self.time == other.time

    def __lt__(self, other: Self):
        return self.time < other.time

    def __hash__(self):
        return id(self)

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __iter__(self):
        return iter(self.__dict__.items())

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def set_attributes(self, **kwargs):
        """Set keyword arguments as instance attributes and values.

        Keyword Args:
            **kwargs: Instance attributes and values as keyword arguments
        """
        [setattr(self, i, j) for i, j in kwargs.items()]

    def is_bullish(self) -> bool:
        """A simple check to see if the candle is bullish.

        Returns:
            bool: True or False
        """
        return self.close >= self.open

    def is_bearish(self) -> bool:
        """A simple check to see if the candle is bearish.

        Returns:
            bool: True or False
        """
        return self.close < self.open

    def dict(self, *, exclude: set = None, include: set = None) -> dict:
        """
        Returns a dictionary of the instance attributes.

        Args:
            exclude: A set of attributes to exclude from the dictionary. Defaults to None.
            include: A set of attributes to include in the dictionary. Defaults to None.

        Returns: dict
        """
        exclude = exclude or set()
        include = include or set()
        keys = include or set(self.__dict__.keys()).difference(exclude)
        return {k: v for k, v in self if k in keys}

    def to_series(self) -> Series:
        """Returns a Series Object"""
        return Series(self.dict(exclude={"Index", "index"}))


class Candles:
    """An iterable container class of Candle objects in chronological order.

    Attributes:
        index (DatetimeIndex): DatetimeIndex of the DataFrame object.
        Index (Series['int']): A pandas Series of the indexes of all candles in the object:
        time (Series['float']): A pandas Series of the time of all candles in the object.
        open (Series[float]): A pandas Series of the opening price of all candles in the object.
        high (Series[float]): A pandas Series of the high price of all candles in the object.
        low (Series[float]):  A pandas Series of the low price of all candles in the object.
        close (Series[float]):  A pandas Series of the closing price of all candles in the object.
        tick_volume (Series[float]):  A pandas Series of the tick volume of all candles in the object.
        real_volume (Series[float]): A pandas Series of the real volume of all candles in the object.
        spread (Series[float]): A pandas Series of the spread of all candles in the object.
        timeframe (TimeFrame): The timeframe of the candles in the object.
        Candle (Type[Candle]): The Candle class for representing the candles in the object.

    properties:
        data (DataFrame): A pandas DataFrame of all candles in the object.

    Notes:
        The candle class can be customized by subclassing the Candle class and passing the subclass as the candle
         keyword argument, or defining it on the class body as a class attribute.
    """
    index: DatetimeIndex
    Index: Series
    time: Series
    open: Series
    high: Series
    low: Series
    close: Series
    tick_volume: Series
    real_volume: Series
    spread: Series
    Candle: Type[Candle]
    timeframe: TimeFrame
    _data: DataFrame

    def __init__(self, *, data: DataFrame | Self | Iterable, flip=False, candle_class: Candle = None):
        """A container class of Candle objects in chronological order.

        Args:
            data (DataFrame|Candles|Iterable): A pandas dataframe, a Candles object or any suitable iterable

        Keyword Args:
            flip (bool): Reverse the chronological order of the candles to the most recent first. Defaults to False.
            candle_class: A subclass of Candle to use as the candle class. Defaults to Candle.
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

    def __repr__(self):
        return repr(self._data)

    def __len__(self):
        return len(self._data.index)

    def __contains__(self, item: Candle):
        return item.time == self[item.Index].time

    def __getitem__(self, index: slice | int | str) -> Self | Series | Candle:
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

    def __setitem__(self, index, value: Series):
        if isinstance(value, Series):
            self._data[index] = value
            return
        raise TypeError(f"Expected Series got {type(value)}")

    def __getattr__(self, item):
        if item in self._data.columns:
            return self._data[item]

        if item == "index":
            return self._data.index

        if item == "Index":
            return Series(range(len(self._data)))
        raise AttributeError(f"Attribute {item} not defined on class {self.__class__.__name__}")

    def __reversed__(self):
        for index, row in enumerate(iter(self._data[::-1].iloc)):
            row = row.to_dict()
            index = len(self._data) - index - 1
            row["Index"] = index
            row["index"] = self._data.index[index]
            yield self.Candle(**row)

    def __iter__(self):
        for index, row in enumerate(iter(self._data.iloc)):
            row = row.to_dict()
            row["Index"] = index
            row["index"] = self._data.index[index]
            yield self.Candle(**row)

    @property
    def timeframe(self):
        tf = self.time.iloc[1] - self.time.iloc[0]
        return TimeFrame.get_timeframe(abs(tf))

    @property
    def columns(self) -> DataFrame:
        return self._data.columns

    @property
    def ta(self):
        """Access to the pandas_ta library for performing technical analysis on the underlying data attribute.

        Returns:
            pandas_ta: The pandas_ta library
        """
        return self._data.ta

    @property
    def ta_lib(self):
        """Access to the ta library for performing technical analysis. Not dependent on the underlying data attribute.

        Returns:
            ta: The ta library
        """
        return ta

    @property
    def data(self) -> DataFrame:
        """The original data passed to the class as a pandas DataFrame"""
        return self._data

    def rename(self, inplace=True, **kwargs) -> Self:
        """Rename columns of the candles class.

        Keyword Args:
            inplace (bool): Rename the columns inplace or return a new instance of the class with the renamed columns
            **kwargs: The new names of the columns

        Returns:
            Candles: A new instance of the class with the renamed columns if inplace is False else the modified instance
        """
        res = self._data.rename(columns=kwargs, inplace=inplace)
        return self if inplace else self.__class__(data=res)

    def __iadd__(self, other: Self) -> Self:
        """Perform in place addition of candles"""
        data_copy = self._data.copy()
        other = other._data
        for index, row in zip(other.index, iter(other.iloc)):
            data_copy.loc[index] = row
        self._data = data_copy.sort_index()
        return self

    def __add__(self, other: Self) -> Self:
        """Add two candles object and return a new one"""
        data = self._data.copy()
        for index, row in zip(other._data.index, iter(other._data.iloc)):
            data.loc[index] = row
        return self.__class__(data=data.sort_index())

    def add(self, obj: DataFrame | Series | Candle) -> Self:
        """Add new row(s) to the candles class."""
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
        """
        Create a plot of the candles

        Args:
            subplots (dict): Subplots to bed added to the main plot
            span (int): Last 'n' candles to be used for making the subplot
            filename (str): A filename to saved the plot
            **kwargs: Kwargs to be passed to the plot
        """
        type_ = kwargs.pop("type", "candle")
        subplots = subplots or []
        span = 0 if span is None else span
        data = self._data[-span:]
        if filename and not kwargs.get("savefig"):
            kwargs["savefig"] = self.config.plots_dir / filename

        mpf.plot(data, type=type_, addplot=subplots, **kwargs)

    def make_subplot(self, *, column: str | list[str], span: int = None, **kwargs) -> dict:
        """
        Create a subplot
        Args:
            column (list[str] | str): Name of columns for the subplot
            span (int): Last 'n' candles to be used for making the subplot
            **kwargs: Keywords arguments to pass to the subplot

        Returns:
            dict: Subplots
        """
        column = column if isinstance(column, list) else [column]
        span = 0 if span is None else span
        data = self._data[-span:]
        data = data[column]
        return mpf.make_addplot(data, **kwargs)
