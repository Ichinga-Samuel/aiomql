# -*- coding: utf-8 -*-
from multiprocessing import cpu_count
from dataclasses import dataclass, field

from pandas_ta._typing import Int, List
from pandas_ta.utils._time import get_time


__all__ = [
    "Study",
    "AllStudy",
    "CommonStudy"
]



# Study DataClass
@dataclass
class Study:
    """Study DataClass
    Class to name and group indicators for processing.

    Parameters:
        name (str): Name.
        ta (list of dicts): i.e [{"kind": "ema", "length", 50}]
        cores (int): The number cores to use for multiprocessing.
            Default: ```cpu_count()```
        description (str): Description of what the Study. Default: ```""```
        created (str): DateTime String at creation.
            Default: Automatically generated.

    Returns:
        (DataClass): The Study to be processed by ```df.ta.study()```

    Example: All or Common Study
        Run
        ```py
        # All
        df.ta.study(ta.AllStudy, **kwargs)

        # Common
        df.ta.study(ta.CommonStudy, **kwargs)
        ```

    Example: Custom Study
        Create
        ```py
        DemoStudy = ta.Study(
            name="Demo Study",
            description="Example Study Group",
            cores=0,  # Usually faster than multiprocessing
            ta = [
                {"kind": "sma", "length": 200},
                {"kind": "sma", "close": "volume", "length": 50},
                {"kind": "bbands", "length": 20},
                {"kind": "rsi"},
                {"kind": "macd", "fast": 8, "slow": 21},
                {"kind": "sma", "close": "volume", "length": 20, "prefix": "VOLUME"}
            ]
        ```

        Run
        ```py
        df.ta.study(DemoStudy, **kwargs)
        ```

    Note:
        * See [also](../getting-started/usage.md) the Pandas TA
          "Study" Examples
        * Case-insensitive "All" is reserved.

    Warning: Multiprocessing
        **Not recommended** for:

        * Small sets of indicators
        * Indicator chains
    """
    name: str
    ta: List = field(default_factory=list)
    cores: Int  = cpu_count()
    description: str = ""
    created: str = get_time(to_string=True)


    def __post_init__(self):
        if isinstance(self.cores, int) and self.cores >= 0 and self.cores <= cpu_count():
            self.cores = int(self.cores)

        req_args = ["[X] Study requires the following argument(s):"]

        if self._is_name():
            req_args.append(
                ' - name. Must be a string. Example: "My TA". Note: "all" is reserved.')

        if self.ta is None:
            self.ta = None
        elif not self._is_ta():
            s = " - ta. Format is a list of dicts. Example: [{'kind': 'sma', 'length': 10}]"
            s += "\n       Check the indicator for the correct arguments if you receive this error."
            req_args.append(s)

        if len(req_args) > 1:
            [print(_) for _ in req_args]
            return None


    def _is_name(self):
        return self.name is None or not isinstance(self.name, str)


    def _is_ta(self):
        if isinstance(self.ta, list) and self.total_ta() > 0:
            # Check that all elements of the list are dicts.
            # Does not check if the dicts values are valid indicator kwargs
            # User must check indicator documentation for all indicators args.
            return all([isinstance(_, dict) and len(_.keys()) > 0 for _ in self.ta])

        return False


    def total_ta(self):
        return len(self.ta) if self.ta is not None else 0



# All Study
AllStudy = Study(
    name="All",
    description="All the indicators with their default settings. Pandas TA default.",
    ta=None,
)

# Default (Example) Study.
CommonStudy = Study(
    name="Common Price and Volume SMAs",
    description="Common Price SMAs: 10, 20, 50, 200 and Volume SMA: 20.",
    cores=0,
    ta=[
        {"kind": "sma", "length": 10},
        {"kind": "sma", "length": 20},
        {"kind": "sma", "length": 50},
        {"kind": "sma", "length": 200},
        {"kind": "sma", "close": "volume", "length": 20, "prefix": "VOL"}
    ]
)
