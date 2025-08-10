# -*- coding: utf-8 -*-
from numpy import nan
from pandas import DataFrame, Series
from pandas_ta._typing import DictLike, Int, IntFloat
from pandas_ta.overlap import ema, linreg, sma
from pandas_ta.trend import decreasing, increasing
from pandas_ta.utils import (
    simplify_columns,
    unsigned_differences,
    v_bool,
    v_mamode,
    v_offset,
    v_pos_default,
    v_series
)
from pandas_ta.volatility import bbands, kc
from .mom import mom



def squeeze(
    high: Series, low: Series, close: Series,
    bb_length: Int = None, bb_std: IntFloat = None,
    kc_length: Int = None, kc_scalar: IntFloat = None,
    mom_length: Int = None, mom_smooth: Int = None,
    use_tr: bool = None, mamode: str = None,
    prenan: bool = None,
    offset: Int = None, **kwargs: DictLike
) -> DataFrame:
    """Squeeze

    This indicator, based on John Carter's "TTM Squeeze" indicator, attempts
    identify momentum using volatility.

    Sources:
        * "Mastering the Trade" (chapter 11), John Carter
        * [thinkorswim](https://tlc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/T-U/TTM-Squeeze)
        * [tradestation](https://tradestation.tradingappstore.com/products/TTMSqueeze)
        * [tradingview](https://www.tradingview.com/scripts/lazybear/)

    Parameters:
        high (pd.Series): ```high``` Series
        low (pd.Series): ```low``` Series
        close (pd.Series): ```close``` Series
        bb_length (int): BB period. Default: ```20```
        bb_std (float): BB Std. Dev. Default: ```2```
        kc_length (int): KC period. Default: ```20```
        kc_scalar (float): KC scalar. Default: ```1.5```
        mom_length (int): Momentum Period. Default: ```12```
        mom_smooth (int): Momentum Smoothing period. Default: ```6```
        mamode (str): One of: "ema" or "sma". Default: ```"sma"```
        prenan (bool): Apply prenans. Default: ```False```
        offset (int): Post shift. Default: ```0```

    Other Parameters:
        tr (value): Use True Range for Keltner Channels. Default: ```True```
        asint (bool): Returns as ```Int```. Default: ```True```
        lazybear (value): LazyBear's TradingView. Default: ```False```
        detailed (value): Extra detailed. Default: ```False```
        fillna (value): ```pd.DataFrame.fillna(value)```

    Returns:
        (pd.DataFrame):
            * Default: 4 columns
            * Detailed: 10 columns

    Note: Volatility
        * Increasing: ```kc``` and ```bbands``` difference increases
        * Decreasing: ```kc``` and ```bbands```  difference decreases
    """
    # Validate
    bb_length = v_pos_default(bb_length, 20)
    kc_length = v_pos_default(kc_length, 20)
    mom_length = v_pos_default(mom_length, 12)
    mom_smooth = v_pos_default(mom_smooth, 6)
    _length = max(bb_length, kc_length, mom_length, mom_smooth) + 1
    high = v_series(high, _length)
    low = v_series(low, _length)
    close = v_series(close, _length)

    if high is None or low is None or close is None:
        return

    bb_std = v_pos_default(bb_std, 2.0)
    kc_scalar = v_pos_default(kc_scalar, 1.5)
    mamode = v_mamode(mamode, "sma")
    prenan = v_bool(prenan, False)
    offset = v_offset(offset)

    use_tr = kwargs.pop("tr", True)
    asint = kwargs.pop("asint", True)
    detailed = kwargs.pop("detailed", False)
    lazybear = kwargs.pop("lazybear", False)

    # Calculate
    bbd = bbands(close, length=bb_length, std=bb_std, mamode=mamode)
    kch = kc(
        high, low, close, length=kc_length, scalar=kc_scalar,
        mamode=mamode, tr=use_tr
    )

    # Simplify KC and BBAND column names for dynamic access
    bbd.columns = simplify_columns(bbd)
    kch.columns = simplify_columns(kch)

    if lazybear:
        highest_high = high.rolling(kc_length).max()
        lowest_low = low.rolling(kc_length).min()
        avg_ = 0.5 * (0.5 * (highest_high + lowest_low) + kch.b)

        squeeze = linreg(close - avg_, length=kc_length)

    else:
        momo = mom(close, length=mom_length)
        if mamode.lower() == "ema":
            squeeze = ema(momo, length=mom_smooth)
        else:  # "sma"
            squeeze = sma(momo, length=mom_smooth)

    # Classify Squeezes
    squeeze_on = (bbd.l > kch.l) & (bbd.u < kch.u)
    squeeze_off = (bbd.l < kch.l) & (bbd.u > kch.u)
    no_squeeze = ~squeeze_on & ~squeeze_off

    # Offset
    if offset != 0:
        squeeze = squeeze.shift(offset)
        squeeze_on = squeeze_on.shift(offset)
        squeeze_off = squeeze_off.shift(offset)
        no_squeeze = no_squeeze.shift(offset)

    # Fill
    if "fillna" in kwargs:
        squeeze.fillna(kwargs["fillna"], inplace=True)
        squeeze_on.fillna(kwargs["fillna"], inplace=True)
        squeeze_off.fillna(kwargs["fillna"], inplace=True)
        no_squeeze.fillna(kwargs["fillna"], inplace=True)

    # Name and Category
    _props = "" if use_tr else "hlr"
    _props += f"_{bb_length}_{bb_std}_{kc_length}_{kc_scalar}"
    _props += "_LB" if lazybear else ""
    squeeze.name = f"SQZ{_props}"

    if asint:
        squeeze_on = squeeze_on.astype(int)
        squeeze_off = squeeze_off.astype(int)
        no_squeeze = no_squeeze.astype(int)

    if prenan:
        nanlength = max(bb_length, kc_length) - 2
        squeeze_on[:nanlength] = nan
        squeeze_off[:nanlength] = nan
        no_squeeze[:nanlength] = nan

    data = {
        squeeze.name: squeeze,
        f"SQZ_ON": squeeze_on,
        f"SQZ_OFF": squeeze_off,
        f"SQZ_NO": no_squeeze
    }
    df = DataFrame(data, index=close.index)
    df.name = squeeze.name
    df.category = squeeze.category = "momentum"

    # More Detail
    if detailed:
        pos_squeeze = squeeze[squeeze >= 0]
        neg_squeeze = squeeze[squeeze < 0]

        pos_inc, pos_dec = unsigned_differences(pos_squeeze, asint=True)
        neg_inc, neg_dec = unsigned_differences(neg_squeeze, asint=True)

        pos_inc *= squeeze
        pos_dec *= squeeze
        neg_dec *= squeeze
        neg_inc *= squeeze

        pos_inc.replace(0, nan, inplace=True)
        pos_dec.replace(0, nan, inplace=True)
        neg_dec.replace(0, nan, inplace=True)
        neg_inc.replace(0, nan, inplace=True)

        sqz_inc = squeeze * increasing(squeeze)
        sqz_dec = squeeze * decreasing(squeeze)
        sqz_inc.replace(0, nan, inplace=True)
        sqz_dec.replace(0, nan, inplace=True)

        # Handle fills
        if "fillna" in kwargs:
            sqz_inc.fillna(kwargs["fillna"], inplace=True)
            sqz_dec.fillna(kwargs["fillna"], inplace=True)
            pos_inc.fillna(kwargs["fillna"], inplace=True)
            pos_dec.fillna(kwargs["fillna"], inplace=True)
            neg_dec.fillna(kwargs["fillna"], inplace=True)
            neg_inc.fillna(kwargs["fillna"], inplace=True)

        df[f"SQZ_INC"] = sqz_inc
        df[f"SQZ_DEC"] = sqz_dec
        df[f"SQZ_PINC"] = pos_inc
        df[f"SQZ_PDEC"] = pos_dec
        df[f"SQZ_NDEC"] = neg_dec
        df[f"SQZ_NINC"] = neg_inc

    return df
