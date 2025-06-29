"""Module for working with price ticks."""

from typing import Iterable, Self
from datetime import datetime

import pandas as pd
from pandas import DataFrame, Series
import pandas_ta as ta

from ..core.constants import TickFlag


class Tick:
    """Price Tick of a Financial Instrument.

    Attributes:
        time (int): Time of the last prices update for the symbol
        bid (float): Current Bid price
        ask (float): Current Ask price
        last (float): Price of the last deal (Last)
        volume (float): Volume for the current Last price
        time_msc (int): Time of the last prices update for the symbol in milliseconds
        flags (TickFlag): Tick flags
        volume_real (float): Volume for the current Last price
        Index (int): Custom attribute representing the position of the tick in a sequence.
        index (int): Index of the tick in the input dataframe object.
    """
    time: float
    bid: float
    ask: float
    last: float
    volume: float
    time_msc: float
    flags: TickFlag
    volume_real: float
    index: int | float
    Index: int

    def __init__(self, **kwargs):
        """Initialize the Tick class. Set attributes from keyword arguments. bid, ask, last and volume must be
        present"""
        if not all(key in kwargs for key in ["bid", "ask", "last", "volume"]):
            raise ValueError("bid, ask, last and volume, time must be present in the keyword arguments")
        self.time = kwargs.pop("time", datetime.now().timestamp())
        self.time_msc = kwargs.pop("time_msc", self.time * 1000)
        self.Index = kwargs.pop("Index", 0)
        self.index = kwargs.pop("index", self.time_msc)
        self.set_attributes(**kwargs)

    def __repr__(self):
        return (
            "%(class)s(Index=%(Index)s, time=%(time)s, bid=%(bid)s, ask=%(ask)s, last=%(last)s, volume=%(volume)s, index=%(index)s)"
            % {
                "class": self.__class__.__name__,
                "time": self.time,
                "bid": self.bid,
                "ask": self.ask,
                "last": self.last,
                "volume": self.volume,
                "index": self.index,
                "Index": self.Index,
            }
        )

    def __eq__(self, other: Self):
        return self.time_msc == other.time_msc

    def __lt__(self, other: Self):
        return self.time_msc < other.time_msc

    def __hash__(self):
        return hash(self.time_msc)

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

    def dict(self, exclude: set = None, include: set = None) -> dict:
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
        return {k: v for k, v in self.__dict__.items() if k in keys}

    def set_attributes(self, **kwargs):
        """Set attributes from keyword arguments"""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_series(self) -> pd.Series:
        """Returns a Series Object"""
        return Series(self.dict(exclude={"Index", "index"}))

class Ticks:
    """Container class for price ticks. Arrange in chronological order. Supports iteration, slicing and assignment"""
    time: Series
    bid: Series
    ask: Series
    last: Series
    volume: Series
    time_msc: Series
    flags: Series
    volume_real: Series
    Index: Series
    index: Series

    def __init__(self, *, data: DataFrame | Iterable | Self, flip=False):
        """Initialize the Ticks class. Creates a DataFrame of price ticks from the data argument.

        Args:
            data (DataFrame | Iterable): Dataframe of price ticks or any iterable object that can be converted to a
                pandas DataFrame
            flip (bool): If flip is True reverse data chronological order.
        """
        if isinstance(data, DataFrame):
            data = data
        elif isinstance(data, type(self)):
            data = DataFrame(data.data)
        elif isinstance(data, Iterable):
            data = DataFrame(data)
        else:
            raise ValueError(f"Cannot create DataFrame from object of {type(data)}")
        self._data = data.iloc[::-1] if flip else data

        if 'time_msc' in self._data.columns:
            self._data.index = self._data.time_msc

    def __repr__(self):
        return repr(self._data)

    def __len__(self):
        return self._data.shape[0]

    def __contains__(self, item: Tick) -> bool:
        return item.time_msc == self[item.Index].time_msc

    def __getattr__(self, item):
        if item in list(self._data.columns.values):
            return self._data[item]

        if item == "index":
            return self._data.index

        if item == "Index":
            return Series(range(len(self._data)))
        raise AttributeError(f"Attribute {item} not defined on class {self.__class__.__name__}")

    def __getitem__(self, index) -> Tick | Self:
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
            tick = self._data.iloc[index]
            Index = index if index >= 0 else len(self) + index
            _index = self._data.index[index]
            return Tick(**tick, Index=Index, index=_index)

        raise TypeError(f"Expected int, slice or str got {type(index)}")

    def __setitem__(self, index, value: Series):
        if isinstance(value, Series):
            self._data[index] = value
            return
        raise TypeError(f"Expected Series got {type(value)}")

    def __reversed__(self):
        for index, row in enumerate(iter(self._data[::-1].iloc)):
            row = row.to_dict()
            index = len(self._data) - index - 1
            row["Index"] = index
            row["index"] = self._data.index[index]
            yield Tick(**row)

    def __iter__(self):
        for index, row in enumerate(iter(self._data.iloc)):
            row = row.to_dict()
            row["Index"] = index
            row["index"] = self._data.index[index]
            yield Tick(**row)

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
        """DataFrame of price ticks arranged in chronological order."""
        return self._data

    def rename(self, inplace=True, **kwargs) -> Self | None:
        """Rename columns of the candle class.

        Keyword Args:
            inplace (bool): Rename the columns inplace or return a new instance of the class with the renamed columns
            **kwargs: The new names of the columns

        Returns:
            Ticks: A new instance of the class with the renamed columns if inplace is False.
            None: If inplace is True
        """
        res = self._data.rename(columns=kwargs, inplace=inplace)
        return res if inplace else self.__class__(data=res)

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

    def add(self, obj: DataFrame | Series | Tick) -> Self:
        """Add new row(s) to the candles class."""
        if isinstance(obj, Series):
            self._data.loc[obj.index] = obj
            self._data = self._data.sort_index()
            return self
        elif isinstance(obj, DataFrame):
            data = self._data.copy()
            for index, row in zip(obj.index, iter(obj.iloc)):
                index = index
                data.loc[index] = row
            self._data = data.sort_index()
            return self
        elif isinstance(obj, Tick):
            self._data.loc[obj.index] = obj.to_series()
            self._data = self._data.sort_index()
            return self
        else:
            raise TypeError("Expected Series, DataFrame or Candle, got {}".format(type(obj)))
