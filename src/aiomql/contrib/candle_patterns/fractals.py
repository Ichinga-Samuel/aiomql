from ...lib.candle import Candle, Candles


def find_bearish_fractal(candles: Candles) -> Candle | None:
    """Given a candles object, find the most recent bearish fractal."""
    for i in range(len(candles) - 3, 1, -1):
        if candles[i].high > max(candles[i - 1].high, candles[i + 1].high, candles[i - 2].high, candles[i + 2].high):
            return candles[i]


def find_bullish_fractal(candles: Candles) -> Candle | None:
    """Given a candles object, find the most recent bullish fractal."""
    for i in range(len(candles) - 3, 1, -1):
        if candles[i].low < min(candles[i - 1].low, candles[i + 1].low, candles[i - 2].low, candles[i + 2].low):
            return candles[i]
