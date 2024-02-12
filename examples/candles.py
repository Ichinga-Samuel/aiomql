import asyncio
from aiomql import Symbol, TimeFrame, Account, Candle, Candles


async def main():
    """Example of using the Candle and Candles classes.
    The candle class is a single price bar. Holding the OHLCV data for a single price bar.
    The Candles class is a container of Candle objects. It is an Iterable of Candle objects.
    It can be sliced and indexed. It can also be accessed with keywords.
    It is a wrapper around a pandas DataFrame. Which is what it uses to store the data.
    """
    async with Account():
        sym = Symbol(name="EURUSD")

        # Get EURUSD price bars for the past 48 hours
        candles: Candles = await sym.copy_rates_from_pos(timeframe=TimeFrame.H1, count=48, start_position=0)

        # get size of candles
        print(len(candles))  # 48

        # get the latest candle by accessing the last one.
        last: Candle = candles[-1]  # A Candle object
        print(type(last))
        print(last.Index)

        # slicing returns a Candles object
        half = candles[24:]
        print(type(half))
        print(len(half))

        close = candles['close']  # close price of all the candles as a pandas series
        print(type(close))
        print(close)

        # compute ema using pandas ta
        candles.ta.ema(length=34, append=True, fillna=0)
        # rename the column to ema
        candles.rename(EMA_34='ema')

        # use talib to compute crossover. This returns a series object that is not part of the candles object.
        closeXema = candles.ta_lib.cross(candles.close, candles.ema)

        # add to the candles
        candles['closeXema'] = closeXema
        print(candles)

        # iterate over the first 5 candles
        for candle in candles[:5]:
            print(candle.open, candle.Index)


asyncio.run(main())
