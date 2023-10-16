import logging

from aiomql.lib import FingerTrap
from aiomql import Bot, Account, ForexSymbol

logging.basicConfig(level=logging.INFO)


def build_bot():
    # Either initialize an account here with your login details here or set them in the aiomql.json file.
    # acc = Account(login=1111111111, password='*******', server='Deriv-Demo')
    bot = Bot()

    # Prebuilt strategy from the library.
    # Disclaimer: These strategy is only for demonstration purposes.
    params = {'trend_candles_count': 500}
    st1 = FingerTrap(symbol=ForexSymbol(name='GBPUSD'), params=params)
    st3 = FingerTrap(symbol=ForexSymbol(name='AUDUSD'), params=params)
    st4 = FingerTrap(symbol=ForexSymbol(name='USDCAD'), params=params)
    st5 = FingerTrap(symbol=ForexSymbol(name='USDJPY'), params=params)
    st6 = FingerTrap(symbol=ForexSymbol(name='EURGBP'), params=params)
    bot.add_strategies([st1, st3, st4, st5, st6])
    bot.execute()


build_bot()
