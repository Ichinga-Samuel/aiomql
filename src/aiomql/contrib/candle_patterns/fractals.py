from aiomql import Candle, Candles

from ...utils.change import percentage_difference


def is_bullish_fractal(candles: Candles) -> tuple[bool, Candle|None]:
    """Check if the candles form a five-candle bullish fractal"""
    if len(candles) < 5:
        return False, None

    # find the two candles by the left and right of the middle candle
    # from left to right; oldest to most recent
    first_left, second_left = candles[-5], candles[-4]
    first_right, second_right = candles[-2], candles[-1]
    center = candles[-3]
    if not ((first_left.low > second_left.low > center.low < first_right.low < second_right.low)
            and center.is_bearish() and first_right.is_bullish()):
        return False, None
    return True, center


def is_half_bullish_fractal(candles: Candles) -> tuple[bool, Candle|None]:
    """Check for a partially formed bullish fractal"""
    if len(candles) < 4:
        return False, None

    # find the two candles by the left and right of the current candle
    # from left to right; oldest to most recent
    first_left, second_left = candles[-4], candles[-3]
    first_right = candles[-1]
    center = candles[-3]
    if not ((first_left.low > second_left.low > center.low < first_right.low) and center.is_bearish() and first_right.is_bullish()):
        return False, None
    return True, center


def is_half_bearish_fractal(candles: Candles) -> tuple[bool, Candle|None]:
    if len(candles) < 4:
        return False, None

    # find the two candles by the left and right of the current candle
    # from left to right; oldest to most recent
    first_left, second_left = candles[-4], candles[-3]
    first_right = candles[-1]
    center = candles[-2]
    if not ((first_left.high < second_left.high < center.high > first_right.high) and center.is_bullish() and first_right.is_bearish()):
        return False, None
    return True, center


def is_bearish_fractal(candles: Candles) -> tuple[bool, Candle|None]:
    """Check if the candles form a bearish fractal"""
    if len(candles) < 5:
        return False, None
    # find the two candles by the left and right of the middle candle
    # from left to right; oldest to most recent
    first_left, second_left = candles[-5], candles[-4]
    first_right, second_right = candles[-2], candles[-1]
    center = candles[-3]
    if not ((first_left.high < second_left.high < center.high > first_right.high > second_right.high) and
            center.is_bullish() and first_right.is_bearish()):
        return False, None
    return True, center


def is_double_bullish_fractal(candles: Candles, tolerance: float = 1) -> tuple[bool, Candle|None]:
    """Check if the candles form a double bullish fractal"""
    if len(candles) < 4:
        return False, None

    # find the two candles on the left and right
    # from left to right; oldest to most recent
    left, right = candles[-4], candles[-1]
    center_left, center_right = candles[-3], candles[-2]
    if not (percentage_difference(center_left.low, center_right.low) <= tolerance):
        return False, None
    if not (center_left.is_bearish() and center_right.is_bullish()):
        return False, None
    if not (left.low > center_left.low and center_right.low < right.low):
        return False, None
    return True, min(center_left, center_right, key=lambda c: c.low)



def is_double_bearish_fractal(candles: Candles, tolerance: float = 1) -> tuple[bool, Candle|None]:
    """Check if the candles form a double bearish fractal"""
    if len(candles) < 4:
        return False, None

    # find the two candles on the left and right
    # from left to right; oldest to most recent
    left, right = candles[-4], candles[-1]
    center_left, center_right = candles[-3], candles[-2]
    if not (percentage_difference(center_left.high, center_right.high) <= tolerance):
        return False, None
    if not (center_left.is_bullish() and center_right.is_bearish()):
        return False, None
    if not (left.high < center_left.high and center_right.high > right.high):
        return False, None
    return True, max(center_left, center_right, key=lambda c: c.high)


def find_bullish_fractal(candles: Candles, swing_number: int = 1, min_price: float = None)  -> tuple[Candle, Candles] | None:
    """Find a bullish fractal pattern"""
    fractal_candles: Candles
    swing_candle: Candle | None = None
    min_price: float = min_price or candles[-1].low

    for c in reversed(candles):
        fractal_candles = candles[c.Index: c.Index + 5]
        ok, candle = is_bullish_fractal(fractal_candles)
        if ok and ((swing_candle is not None and candle.low < swing_candle.low) or swing_candle is None) and candle.low < min_price:
            swing_number -= 1
            swing_candle = candle
        if swing_number <= 0:
            return swing_candle, fractal_candles
        continue
    return None


def find_bearish_fractal(candles: Candles, swing_number: int = 1, max_price: float = None) -> tuple[Candle, Candles] | None:
    """Find a bearish fractal pattern"""
    fractal_candles: Candles
    swing_candle: Candle | None = None
    max_price: float = max_price or candles[-1].high

    for c in reversed(candles):
        fractal_candles = candles[c.Index: c.Index + 5]
        ok, candle = is_bearish_fractal(fractal_candles)
        if (ok and ((swing_candle is not None and candle.high > swing_candle.high) or swing_candle is None) and
                candle.high > max_price):
            swing_number -= 1
            swing_candle = candle
        if swing_number <= 0:
            return swing_candle, fractal_candles
        continue
    return None


def find_double_bearish_fractal(candles: Candles, swing_number: int = 1,
                                tolerance: float = 1, max_price: float = None) -> tuple[Candle, Candles] | None:
    """Find double bearish Fractals"""
    fractal_candles: Candles
    swing_candle: Candle | None = None
    max_price: float = max_price or candles[-1].high

    for c in reversed(candles):
        fractal_candles = candles[c.Index: c.Index + 4]
        ok, candle = is_double_bearish_fractal(fractal_candles, tolerance=tolerance)
        if (ok and ((swing_candle is not None and candle.high > swing_candle.high) or swing_candle is None)
                and candle.high > max_price):
            swing_number -= 1
            swing_candle = candle
        if swing_number <= 0:
            return swing_candle, fractal_candles
        continue
    return None


def find_double_bullish_fractal(candles: Candles, swing_number: int = 1,
                                tolerance: float = 1, min_price: float = None) -> tuple[Candle, Candles] | None:
    """Find double bullish Fractals"""
    fractal_candles: Candles
    swing_candle: Candle | None = None
    min_price: float = min_price or candles[-1].low

    for c in reversed(candles):
        fractal_candles = candles[c.Index: c.Index + 4]
        ok, candle = is_double_bullish_fractal(fractal_candles, tolerance=tolerance)
        if (ok and ((swing_candle is not None and candle.low < swing_candle.low) or swing_candle is None)
                and candle.low < min_price):
            swing_number -= 1
            swing_candle = candle
        if swing_number <= 0:
            return swing_candle, fractal_candles
        continue
    return None
