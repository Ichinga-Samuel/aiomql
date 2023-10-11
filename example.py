import asyncio

from aiomql.lib import FingerTrap
from aiomql import Bot, Account, ForexSymbol, Records, RAM, DealTrader


def build_bot():
    # Either initialize an account here with your login details here or set them in the aiomql.json file.
    # acc = Account(login=1111111111, password='*******', server='Deriv-Demo')
    bot = Bot()

    # Prebuilt strategy from the library.
    # Disclaimer: These strategy is only for demonstration purposes.

    ram = RAM(amount=50)
    st1 = FingerTrap(symbol=ForexSymbol(name='Volatility 10 (1s) Index'))
    # st1 = FingerTrap(symbol=ForexSymbol(name='Volatility 50 (1s) Index'))
    # st.trader.ram = ram
    st1.trader.ram = ram

    # st1 = FingerTrap(symbol=ForexSymbol(name='GBPUSD'), params={'trend_candles_count': 500})
    # st3 = FingerTrap(symbol=ForexSymbol(name='AUDUSD'))
    # st4 = FingerTrap(symbol=ForexSymbol(name='USDCAD'))
    # st5 = FingerTrap(symbol=ForexSymbol(name='USDJPY'))
    # st6 = FingerTrap(symbol=ForexSymbol(name='EURGBP'))
    # bot.add_strategies([st, st1, st3, st4, st5, st6])
    # bot.add_strategy(st)
    bot.add_strategy(st1)
    bot.execute()


build_bot()

async def main():
    async with Account():
        res = Records()
        await res.update_records()

# asyncio.run(main())
