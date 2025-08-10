from .maps import EXCHANGE_TZ, RATE, Category, Imports
from .utils import *
from .utils import __all__ as utils_all

# Flat Structure. Supports ta.ema() or ta.overlap.ema()
from .candle import *
from .cycle import *
from .momentum import *
from .overlap import *
from .performance import *
from .statistics import *
from .trend import *
from .volatility import *
from .volume import *
from .candle import __all__ as candle_all
from .cycle import __all__ as cycle_all
from .momentum import __all__ as momentum_all
from .overlap import __all__ as overlap_all
from .performance import __all__ as performance_all
from .statistics import __all__ as statistics_all
from .trend import __all__ as trend_all
from .volatility import __all__ as volatility_all
from .volume import __all__ as volume_all

# Common Averages useful for Indicators
# with a mamode argument, like ta.adx()
from .ma import ma

# Custom External Directory Commands. See help(import_dir)
from .custom import create_dir, import_dir

# Enable "ta" DataFrame Extension
from .core import AnalysisIndicators

__all__ = [
    # "name",
    "EXCHANGE_TZ",
    "RATE",
    "Category",
    "Imports",
    "ma",
    "create_dir",
    "import_dir",
    "AnalysisIndicators",
    "AllStudy",
    "CommonStudy",
]

__all__ += [
    utils_all
    + candle_all
    + cycle_all
    + momentum_all
    + overlap_all
    + performance_all
    + statistics_all
    + trend_all
    + volatility_all
    + volume_all
]
