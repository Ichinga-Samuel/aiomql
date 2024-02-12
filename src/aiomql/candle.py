"""Candle and Candles classes for handling bars from the MetaTrader 5 terminal."""

from typing import Type, TypeVar, Generic, Iterable
from logging import getLogger

from pandas import DataFrame, Series
import pandas_ta as ta

from .core.constants import TimeFrame

logger = getLogger(__name__)


class Candle:
    """A class representing bars from the MetaTrader 5 terminal as a customized class analogous to Japanese
    Candlesticks. You can subclass this class for added customization.

    Attributes:
        time (int): Period start time.
        open (int): Open price
        high (float): The highest price of the period
        low (float): The lowest price of the period
        close (float): Close price
        tick_volume (float): Tick volume
        real_volume (float): Trade volume
        spread (float): Spread
        Index (int): Custom attribute representing the position of the candle in a sequence.
        mid (float): The median of the high and low price.
    """
    time: float
    open: float
    high: float
    low: float
    close: float
    real_volume: float
    spread: float
    tick_volume: float
    Index: int
    mid: float

    def __init__(self, **kwargs):
        """Create a Candle object from keyword arguments. This class must always be instantiated with open, high, low
         and close prices.

        Keyword Args:
            **kwargs: Candle attributes and values as keyword arguments.
        """
        if not all(i in kwargs for i in ['open', 'high', 'low', 'close']):
            raise ValueError("Candle must be instantiated with open, high, low and close prices")
        self.time = kwargs.pop('time', 0)
        self.Index = kwargs.pop('Index', 0)
        self.mid = kwargs.pop('mid', (kwargs['high'] + kwargs['low']) / 2)
        self.set_attributes(**kwargs)

    def __repr__(self):
        return ("%(class)s(Index=%(Index)s, time=%(time)s, open=%(open)s, high=%(high)s, low=%(low)s, close=%(close)s,"
                " mid=%(mid)s)") % {"class": self.__class__.__name__, "open": self.open, "high": self.high,
                                    "low": self.low, "close": self.close, "time": self.time, "mid": self.mid,
                                    'Index': self.Index}

    def __str__(self):
        return self.dict()

    def __eq__(self, other: "Candle"):
        return self.time == other.time

    def __hash__(self):
        return hash(self.time)

    def __lt__(self, other: "Candle"):
        return self.time < other.time

    def __gt__(self, other: "Candle"):
        return self.time > other.time

    def __getitem__(self, item):
        return self.__dict__[item]

    def set_attributes(self, **kwargs):
        """Set keyword arguments as instance attributes

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
        return self.open > self.close

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


_Candle = TypeVar("_Candle", bound=Candle)
_Candles = TypeVar("_Candles", bound="Candles")


class Candles(Generic[_Candle]):
    """An iterable container class of Candle objects in chronological order.

    Attributes:
        Index (Series['int']): A pandas Series of the indexes of all candles in the object.
        time (Series['int']): A pandas Series of the time of all candles in the object.
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
    Index: Series
    time: Series
    open: Series
    high: Series
    low: Series
    close: Series
    tick_volume: Series
    real_volume: Series
    spread: Series
    mid: Series
    Candle: Type[Candle]
    timeframe: TimeFrame
    _data: DataFrame

    def __init__(self, *, data: DataFrame | _Candles | Iterable, flip=False, candle_class: Type[_Candle] = None):
        """A container class of Candle objects in chronological order.

        Args:
            data (DataFrame|Candles|Iterable): A pandas dataframe, a Candles object or any suitable iterable

        Keyword Args:
            flip (bool): Reverse the chronological order of the candles to the oldest first. Defaults to False.
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

        self._data = data.loc[::-1].reset_index(drop=True) if flip else data
        if 'mid' not in self._data.columns.values:
            mid = (self._data['high'] + self._data['low']) / 2
            self._data.insert(0, 'mid', mid)
        self.Candle = candle_class or Candle

    def __repr__(self):
        return self._data.__repr__()

    def __len__(self):
        return len(self._data.index)

    def __contains__(self, item: _Candle):
        return item.time == self[item.Index].time

    def __getitem__(self, index) -> _Candle | _Candles | Series:
        if isinstance(index, slice):
            cls = self.__class__
            data = self._data.iloc[index]
            data.reset_index(drop=True, inplace=True)
            return cls(data=data)

        elif isinstance(index, str):
            if index == 'Index':
                return Series(self._data.index)
            return self._data[index]

        elif isinstance(index, int):
            index = index if index >= 0 else len(self) + index
            return self.Candle(**self._data.iloc[index], Index=index)
        raise TypeError(f"Expected int, slice or str got {type(index)}")

    def __setitem__(self, index, value: Series):
        if isinstance(value, Series):
            self._data[index] = value
            return
        raise TypeError(f"Expected Series got {type(value)}")

    def __getattr__(self, item):
        if item in self._data.columns:
            return self._data[item]
        if item == 'Index':
            return Series(self._data.index)
        raise AttributeError(f"Attribute {item} not defined on class {self.__class__.__name__}")

    def __iter__(self):
        return (self.Candle(**row._asdict()) for row in self._data.itertuples())

    def __add__(self, other: _Candles | _Candle):
        other = other.data if isinstance(other, type(self)) else other.dict()
        return self.__class__(data=self._data.append(other.data, ignore_index=True))

    @property
    def timeframe(self):
        tf = self.time[1] - self.time[0]
        return TimeFrame.get(abs(tf))

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

    def rename(self, inplace=True, **kwargs) -> _Candles:
        """Rename columns of the candles class.

        Keyword Args:
            inplace (bool): Rename the columns inplace or return a new instance of the class with the renamed columns
            **kwargs: The new names of the columns

        Returns:
            Candles: A new instance of the class with the renamed columns if inplace is False else the modified instance
        """
        res = self._data.rename(columns=kwargs, inplace=inplace)
        return self if inplace else self.__class__(data=res)
