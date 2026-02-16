"""Tick and Ticks classes for working with price tick data.

This module provides classes for handling tick-level price data from
MetaTrader 5. Includes support for technical analysis via pandas_ta
and various data manipulation operations.

Example:
    Working with ticks::

        ticks = await symbol.copy_ticks_from(date_from=datetime.now(), count=1000)
        print(f"Latest bid: {ticks[-1].bid}")
"""

from typing import Iterable, Self
from datetime import datetime

import pandas as pd
from pandas import DataFrame, Series

from ..ta_libs import pandas_ta_classic as ta
from ..core.constants import TickFlag


class Tick:
    """Price Tick of a Financial Instrument.

    Represents a single price tick from MetaTrader 5, containing bid/ask prices,
    volume data, and timing information. Supports dictionary-like access and
    comparison operations based on timestamp.

    Attributes:
        time (float): Time of the last prices update for the symbol as Unix timestamp.
        bid (float): Current Bid price.
        ask (float): Current Ask price.
        last (float): Price of the last deal (Last).
        volume (float): Volume for the current Last price.
        time_msc (float): Time of the last prices update in milliseconds.
        flags (TickFlag): Tick flags indicating what data changed.
        volume_real (float): Volume for the current Last price with extended accuracy.
        Index (int): Position of the tick in a Ticks sequence (0-based from oldest).
        index (int | float): Index of the tick in the underlying DataFrame, typically time_msc.

    Example:
        Creating a tick from data::

            tick = Tick(bid=1.1234, ask=1.1236, last=1.1235, volume=100)
            print(f"Spread: {tick.ask - tick.bid}")
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
        """Initialize the Tick instance with price and volume data.

        Sets attributes from keyword arguments. The required fields bid, ask,
        last, and volume must be present. Time defaults to current timestamp
        if not provided.

        Args:
            **kwargs: Keyword arguments for tick attributes. Must include:
                - bid (float): Current Bid price.
                - ask (float): Current Ask price.
                - last (float): Price of the last deal.
                - volume (float): Volume for the current Last price.
                Optional arguments include time, time_msc, Index, index,
                flags, and volume_real.

        Raises:
            ValueError: If bid, ask, last, or volume are not provided.
        """
        if not all(key in kwargs for key in ["bid", "ask", "last", "volume"]):
            raise ValueError("bid, ask, last and volume, time must be present in the keyword arguments")
        self.time = kwargs.pop("time", datetime.now().timestamp())
        self.time_msc = kwargs.pop("time_msc", self.time * 1000)
        self.Index = kwargs.pop("Index", 0)
        self.index = kwargs.pop("index", self.time_msc)
        self.set_attributes(**kwargs)

    def __repr__(self) -> str:
        """Return a string representation of the Tick.

        Returns:
            str: A formatted string showing key tick attributes.
        """
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

    def __eq__(self, other: Self) -> bool:
        """Check equality based on millisecond timestamp.

        Args:
            other (Tick): Another Tick instance to compare.

        Returns:
            bool: True if both ticks have the same time_msc.
        """
        return self.time_msc == other.time_msc

    def __lt__(self, other: Self) -> bool:
        """Compare ticks chronologically by millisecond timestamp.

        Args:
            other (Tick): Another Tick instance to compare.

        Returns:
            bool: True if this tick occurred before the other.
        """
        return self.time_msc < other.time_msc

    def __hash__(self) -> int:
        """Return hash based on millisecond timestamp.

        Returns:
            int: Hash value for the tick.
        """
        return hash(self.time_msc)

    def __getitem__(self, item: str):
        """Get an attribute value by name using dictionary-style access.

        Args:
            item (str): Name of the attribute to retrieve.

        Returns:
            Any: The value of the requested attribute.

        Raises:
            KeyError: If the attribute does not exist.
        """
        return self.__dict__[item]

    def __setitem__(self, key: str, value):
        """Set an attribute value using dictionary-style assignment.

        Args:
            key (str): Name of the attribute to set.
            value: Value to assign to the attribute.
        """
        self.__dict__[key] = value

    def __iter__(self):
        """Iterate over the tick's attributes as key-value pairs.

        Yields:
            tuple[str, Any]: Attribute name and value pairs.
        """
        return iter(self.__dict__.items())

    def keys(self):
        """Return the tick's attribute names.

        Returns:
            dict_keys: View of the attribute names.
        """
        return self.__dict__.keys()

    def values(self):
        """Return the tick's attribute values.

        Returns:
            dict_values: View of the attribute values.
        """
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
        """Set multiple attributes from keyword arguments.

        Args:
            **kwargs: Attribute name-value pairs to set on the Tick instance.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_series(self) -> pd.Series:
        """Convert the Tick to a pandas Series.

        Creates a Series from the tick's attributes, excluding the Index
        and index attributes which are positional metadata.

        Returns:
            pd.Series: Series containing the tick's price and volume data.
        """
        return Series(self.dict(exclude={"Index", "index"}))

class Ticks:
    """Container class for price ticks with DataFrame-like functionality.

    Stores and manages a collection of price ticks arranged in chronological
    order. Supports iteration, slicing, indexing, technical analysis via
    pandas_ta, and various data manipulation operations.

    Attributes:
        time (Series): Unix timestamps for each tick.
        bid (Series): Bid prices for each tick.
        ask (Series): Ask prices for each tick.
        last (Series): Last deal prices for each tick.
        volume (Series): Volumes for each tick.
        time_msc (Series): Millisecond timestamps for each tick.
        flags (Series): Tick flags for each tick.
        volume_real (Series): Extended accuracy volumes for each tick.
        Index (Series): Sequential position indices (0-based from oldest).
        index (Series): DataFrame index, typically based on time_msc.

    Example:
        Working with a collection of ticks::

            ticks = await symbol.copy_ticks_from(date_from=datetime.now(), count=1000)
            latest = ticks[-1]  # Get latest tick
            subset = ticks[-100:]  # Get last 100 ticks
            for tick in ticks:
                print(tick.bid, tick.ask)
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
    index: Series

    def __init__(self, *, data: DataFrame | Iterable | Self, flip: bool = False):
        """Initialize the Ticks container from tick data.

        Creates a DataFrame of price ticks from the provided data source.
        The DataFrame is indexed by time_msc if that column is present.

        Args:
            data (DataFrame | Iterable | Ticks): Source data for the ticks.
                Can be a pandas DataFrame, another Ticks instance, or any
                iterable that can be converted to a DataFrame.
            flip (bool): If True, reverse the chronological order of the data.
                Defaults to False.

        Raises:
            ValueError: If data cannot be converted to a DataFrame.
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

    def __repr__(self) -> str:
        """Return a string representation of the Ticks container.

        Returns:
            str: String representation of the underlying DataFrame.
        """
        return repr(self._data)

    def __len__(self) -> int:
        """Return the number of ticks in the container.

        Returns:
            int: Number of ticks.
        """
        return self._data.shape[0]

    def __contains__(self, item: Tick) -> bool:
        """Check if a tick is in the container by comparing time_msc.

        Args:
            item (Tick): Tick to check for membership.

        Returns:
            bool: True if a tick with the same time_msc exists at the given Index.
        """
        return item.time_msc == self[item.Index].time_msc

    def __getattr__(self, item: str):
        """Access DataFrame columns as attributes.

        Provides attribute-style access to the underlying DataFrame columns.
        Special handling for 'index' (DataFrame index) and 'Index' (sequential
        position numbers).

        Args:
            item (str): Name of the column or special attribute.

        Returns:
            Series: The requested column data.

        Raises:
            AttributeError: If the attribute is not a valid column or special name.
        """
        if item in list(self._data.columns.values):
            return self._data[item]

        if item == "index":
            return self._data.index

        if item == "Index":
            return Series(range(len(self._data)))
        raise AttributeError(f"Attribute {item} not defined on class {self.__class__.__name__}")

    def __getitem__(self, index) -> Tick | Self:
        """Retrieve tick(s) by index, slice, or column name.

        Supports multiple access patterns:
        - Integer index: Returns a single Tick object.
        - Slice: Returns a new Ticks container with the sliced data.
        - String: Returns the column Series or special index.

        Args:
            index (int | slice | str): The index, slice, or column name.

        Returns:
            Tick | Ticks | Series: Single Tick, sliced Ticks, or column Series.

        Raises:
            TypeError: If index is not int, slice, or str.

        Example:
            Accessing ticks::

                latest = ticks[-1]  # Get last tick
                subset = ticks[10:20]  # Get ticks 10-19
                bids = ticks['bid']  # Get bid column
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
            tick = self._data.iloc[index]
            Index = index if index >= 0 else len(self) + index
            _index = self._data.index[index]
            return Tick(**tick, Index=Index, index=_index)

        raise TypeError(f"Expected int, slice or str got {type(index)}")

    def __setitem__(self, index: str, value: Series):
        """Set a column in the underlying DataFrame.

        Args:
            index (str): Name of the column to set.
            value (Series): Series data to assign to the column.

        Raises:
            TypeError: If value is not a pandas Series.
        """
        if isinstance(value, Series):
            self._data[index] = value
            return
        raise TypeError(f"Expected Series got {type(value)}")

    def __reversed__(self):
        """Iterate over ticks in reverse chronological order.

        Yields:
            Tick: Each tick from newest to oldest.
        """
        for index, row in enumerate(iter(self._data[::-1].iloc)):
            row = row.to_dict()
            index = len(self._data) - index - 1
            row["Index"] = index
            row["index"] = self._data.index[index]
            yield Tick(**row)

    def __iter__(self):
        """Iterate over ticks in chronological order.

        Yields:
            Tick: Each tick from oldest to newest.
        """
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
        """Perform in-place addition of ticks from another Ticks container.

        Merges ticks from another Ticks instance into this one, updating
        existing entries by index and adding new ones. The result is sorted
        by index.

        Args:
            other (Ticks): Ticks container to merge.

        Returns:
            Ticks: This instance with merged data.
        """
        data_copy = self._data.copy()
        other = other._data
        for index, row in zip(other.index, iter(other.iloc)):
            data_copy.loc[index] = row
        self._data = data_copy.sort_index()
        return self

    def __add__(self, other: Self) -> Self:
        """Combine two Ticks containers and return a new one.

        Creates a new Ticks instance containing data from both containers.
        Entries are merged by index, with later values overwriting earlier
        ones for duplicate indices. The result is sorted by index.

        Args:
            other (Ticks): Ticks container to add.

        Returns:
            Ticks: New Ticks instance with combined data.
        """
        data = self._data.copy()
        for index, row in zip(other._data.index, iter(other._data.iloc)):
            data.loc[index] = row
        return self.__class__(data=data.sort_index())

    def add(self, obj: DataFrame | Series | Tick) -> Self:
        """Add new tick(s) to the container.

        Adds one or more ticks to the container, maintaining sorted order
        by index. Supports adding individual Tick objects, pandas Series,
        or entire DataFrames.

        Args:
            obj (DataFrame | Series | Tick): Data to add. Can be:
                - Tick: A single tick object.
                - Series: A row of tick data.
                - DataFrame: Multiple rows of tick data.

        Returns:
            Ticks: This instance with the added data.

        Raises:
            TypeError: If obj is not a Series, DataFrame, or Tick.

        Example:
            Adding new tick data::

                new_tick = Tick(bid=1.1234, ask=1.1236, last=1.1235, volume=100)
                ticks.add(new_tick)
        """
        if isinstance(obj, Series):
            self._data.loc[obj.time_msc] = obj
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
            raise TypeError("Expected Series, DataFrame or Tick, got {}".format(type(obj)))
