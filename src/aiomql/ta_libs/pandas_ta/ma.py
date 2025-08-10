from pandas import Series
from ._typing import DictLike
from .overlap.dema import dema
from .overlap.ema import ema
from .overlap.fwma import fwma
from .overlap.hma import hma
from .overlap.linreg import linreg
from .overlap.midpoint import midpoint
from .overlap.pwma import pwma
from .overlap.rma import rma
from .overlap.sinwma import sinwma
from .overlap.sma import sma
from .overlap.ssf import ssf
from .overlap.swma import swma
from .overlap.t3 import t3
from .overlap.tema import tema
from .overlap.trima import trima
from .overlap.vidya import vidya
from .overlap.wma import wma


def ma(name: str = None, source: Series = None, **kwargs: DictLike) -> Series:
    """MA Selection Utility

    Available MAs: dema, ema, fwma, hma, linreg, midpoint, pwma, rma,
    sinwma, sma, ssf, swma, t3, tema, trima, vidya, wma.

    Parameters:
        name (str): One of the Available MAs. Default: "ema"
        source (pd.Series): Input Series ```source```.

    Other Parameters:
        kwargs (**kwargs): Additional args for the MA.

    Returns:
        (pd.Series): Selected MA

    Esourceample:
        ```py linenums="0"
        ema8 = ta.ma("ema", df.close, length=8)
        sma50 = ta.ma("sma", df.close, length=50)
        pwma10 = ta.ma("pwma", df.close, length=10, asc=False)
        ```
    """
    _mas = [
        "dema", "ema", "fwma", "hma", "linreg", "midpoint", "pwma", "rma",
        "sinwma", "sma", "ssf", "swma", "t3", "tema", "trima", "vidya", "wma"
    ]
    if name is None and source is None:
        return _mas
    elif isinstance(name, str) and name.lower() in _mas:
        name = name.lower()
    else:  # "ema"
        name = _mas[1]

    if   name == "dema": return dema(source, **kwargs)
    elif name == "fwma": return fwma(source, **kwargs)
    elif name == "hma": return hma(source, **kwargs)
    elif name == "linreg": return linreg(source, **kwargs)
    elif name == "midpoint": return midpoint(source, **kwargs)
    elif name == "pwma": return pwma(source, **kwargs)
    elif name == "rma": return rma(source, **kwargs)
    elif name == "sinwma": return sinwma(source, **kwargs)
    elif name == "sma": return sma(source, **kwargs)
    elif name == "ssf": return ssf(source, **kwargs)
    elif name == "swma": return swma(source, **kwargs)
    elif name == "t3": return t3(source, **kwargs)
    elif name == "tema": return tema(source, **kwargs)
    elif name == "trima": return trima(source, **kwargs)
    elif name == "vidya": return vidya(source, **kwargs)
    elif name == "wma": return wma(source, **kwargs)
    else: return ema(source, **kwargs)
