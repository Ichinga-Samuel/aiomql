"""Module for working with price ticks."""

from typing import Iterable, Self
import time

from pandas import DataFrame, Series
import pandas_ta as ta
import mplfinance as mplt
import pandas as pd

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
    """
    time: float
    bid: float
    ask: float
    last: float
    volume: float
    time_msc: float
    flags: TickFlag
    volume_real: float
    Index: int

    def __init__(self, **kwargs):
        """Initialize the Tick class. Set attributes from keyword arguments. bid, ask, last and volume must be
        present"""
        if not all(key in kwargs for key in ['bid', 'ask', 'last', 'volume']):
            raise ValueError("bid, ask, last and volume, time must be present in the keyword arguments")
        self.Index = kwargs.pop('Index', 0)
        self.time = kwargs.pop('time', time.monotonic())
        self.time_msc = int(self.time * 1000)
        self.set_attributes(**kwargs)

    def __repr__(self):
        return ("%(class)s(Index=%(Index)s, time=%(time)s, bid=%(bid)s, ask=%(ask)s, last=%(last)s, volume=%(volume)s)"
                % {"class": self.__class__.__name__, "time": self.time, "bid": self.bid,
                   "ask": self.ask, "last": self.last, "volume": self.volume, 'Index': self.Index})

    def __eq__(self, other: Self):
        return self.time == other.time

    def __lt__(self, other: Self):
        return self.time < other.time

    def __hash__(self):
        return hash(self.time)

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
            raise ValueError(f'Cannot create DataFrame from object of {type(data)}')
        self._data = data.iloc[::-1] if flip else data

    def __repr__(self):
        return self._data.__repr__()

    def __len__(self):
        return self._data.shape[0]

    def __contains__(self, item: Tick) -> bool:
        return item.time_msc == self[item.Index].time_msc

    def __getattr__(self, item):
        if item in list(self._data.columns.values):
            return self._data[item]
        raise AttributeError(f'Attribute {item} not defined on class {self.__class__.__name__}')

    def __getitem__(self, index) -> Tick | Self:
        if isinstance(index, slice):
            cls = self.__class__
            data = self._data.iloc[index]
            data.reset_index(drop=True, inplace=True)
            return cls(data=data)

        if isinstance(index, str):
            return self._data[index]

        item = self._data.iloc[index]
        return Tick(**item, Index=index)

    def __setitem__(self, index, value: Series):
        if isinstance(value, Series):
            self._data[index] = value
            return
        raise TypeError(f'Expected Series got {type(value)}')

    def __iter__(self):
        return (Tick(**row._asdict()) for row in self._data.itertuples())

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

    def make_addplot(self, *, count: int = 50, columns: list = None, **kwargs) -> dict:
        """
        Make subplots for adding to the main plot

        Args:
            count (int): The numbers of candles to make the addplot for. Defaults to 50.
            columns (list[str]): The columns to make the plot from. Defaults to None.
            **kwargs: Valid arguments for the mplfinance make_addplot function
        """
        columns = columns or []
        data = self._data[-count:]
        data.index = pd.to_datetime(data['time'], unit='s')
        return mplt.make_addplot(data[columns], **kwargs)

    def visualize(self, *, count: int = 50, _type='candle', savefig: str | dict = None, addplot: dict = None,
                  style: str = 'charles', ylabel: str = 'Price', title: str = 'Chart', **kwargs):
        """Visualize the candles using the mplfinance library.
        Args:
            count (int): The number of candles to visualize, counting from behind, i.e the most recent candles.
             Defaults to 50.
            _type: Type of chart, defaults to candle
            savefig (str|dict): The path to save the figure or a dictionary of parameters to pass to the savefig method.
            addplot: Additional plots to add to the chart. Defaults to None. They should match the dimension of the
              original data which is specified via the count parameter.
            style (str): The style of the chart. Defaults to 'charles'.
            ylabel (str): The label of the y-axis. Defaults to 'Price'.
            title (str): The title of the chart. Defaults to 'Chart'.
            kwargs: valid kwargs for the plot function.
        """
        kwargs |= {key: arg for key, arg in (('savefig', savefig), ('addplot', addplot), ('style', style),
                                             ('ylabel', ylabel), ('title', title), ('type', _type)) if arg}
        data = self._data[-count:]
        data.index = pd.to_datetime(data['time'], unit='s')
        mplt.plot(data, **kwargs)
