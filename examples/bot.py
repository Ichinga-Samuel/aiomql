from datetime import time
import logging

from aiomql import Bot, ForexSymbol, FingerTrap, Session, Sessions, RAM, SimpleTrader, TimeFrame

logging.basicConfig(level=logging.INFO)


def build_bot():
    bot = Bot()

    # create sessions for the strategies
    london = Session(name='London', start=8, end=time(hour=15, minute=30), on_end='close_all')
    new_york = Session(name='New York', start=13, end=time(hour=20, minute=30))
    tokyo = Session(name='Tokyo', start=23, end=time(hour=6, minute=30))

    # configure the parameters and the trader for a strategy
    params = {'trend_candles_count': 500, 'fast_period': 8, 'slow_period': 34, 'entry_timeframe': TimeFrame.M5}
    gbpusd = ForexSymbol(name='GBPUSD')
    st1 = FingerTrap(symbol=gbpusd, params=params,
                     trader=SimpleTrader(symbol=gbpusd, ram=RAM(risk=0.05, risk_to_reward=2)),
                     sessions=Sessions(london, new_york))

    # use the default for the other strategies
    st2 = FingerTrap(symbol=ForexSymbol(name='AUDUSD'), sessions=Sessions(tokyo, new_york))
    st3 = FingerTrap(symbol=ForexSymbol(name='USDCAD'), sessions=Sessions(new_york))
    st4 = FingerTrap(symbol=ForexSymbol(name='USDJPY'), sessions=Sessions(tokyo))
    st5 = FingerTrap(symbol=ForexSymbol(name='EURGBP'), sessions=Sessions(london))

    # sessions are not required
    st6 = FingerTrap(symbol=ForexSymbol(name='EURUSD'))

    # add strategies to the bot
    bot.add_strategies([st1, st2, st3, st4, st5, st6])

    bot.execute()


# run the bot
build_bot()
