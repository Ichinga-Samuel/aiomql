import asyncio
from aiomql import Symbol, TimeFrame, Account


async def main():
    async with Account():
        # create a symbol
        sym = Symbol(name="AUDUSD")

        # Get EURUSD price bars for the past 48 hours
        candles = await sym.copy_rates_from_pos(timeframe=TimeFrame.H1, count=48, start_position=0)
        print(len(candles))  # 48

        # get the latest candle by accessing the last one.
        last = candles[-1]  # A Candle object
        print(type(last))
        print(last.time)

        # get the last five hours
        last_five = candles[-5:]  # A Candles object.
        print(type(last_five))
        print(last_five)

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