"""Module for working with price ticks."""

from typing import TypeVar, Iterable
import reprlib

from pandas import DataFrame, Series
import pandas_ta as ta

from .core.constants import TickFlag


Self = TypeVar('Self', bound='Ticks')


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
    time_msc:float
    flags: float
    volume_real:float
    Index: int
    def __init__(self, **kwargs):
        self.time = kwargs.pop('time', 0)
        self.Index = kwargs.pop('Index', 0)
        self.set_attributes(**kwargs)

    def __repr__(self):
        keys = reprlib.repr(', '.join('%s=%s' % (i, j) for i, j in self.__dict__.items()))[1:-1]
        return '%(class)s(%(args)s)' % {'class': self.__class__.__name__, 'args': keys}


    def set_attributes(self, **kwargs):
        """Set attributes from keyword arguments"""
        for key, value in kwargs.items():
            setattr(self, key, value)

_Ticks = TypeVar('_Ticks', bound='Ticks')

class Ticks:
    """Container data class for price ticks. Arrange in chronological order.
    Supports iteration, slicing and assignment

    Args:
        data (DataFrame | tuple[tuple]): Dataframe of price ticks or a tuple of tuples

    Keyword Args:
        flip (bool): If flip is True reverse data chronological order.

    Attributes:
        data: Dataframe Object holding the ticks
    """
    time: Series
    bid: Series
    ask: Series
    last: Series
    volume: Series
    time_msc: Series
    flags: Series
    volume_real: Series
    Index: Series

    def __init__(self, *, data: DataFrame | Iterable, flip=False):
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
        return Tick(Index=index, **item)

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

    def rename(self, inplace=True, **kwargs) -> _Ticks | None :
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
