import logging
import asyncio

from aiomql.lib.bot import Bot
from aiomql.contrib.strategies import FingerTrap, Chaos
from aiomql.contrib.symbols import ForexSymbol


def sample_bot():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    syms = ["Volatility 75 Index", "Volatility 100 Index", "Volatility 50 Index"]
    symbols = [ForexSymbol(name=sym) for sym in syms]
    strategies = [Chaos(symbol=symbol) for symbol in symbols]
    bot = Bot()
    bot.add_coroutine(coroutine=pray_sleep)
    bot.add_strategies(strategies=strategies)
    bot.timeout = 10
    bot.execute()


async def pray_sleep():
    while True:
        print("I'm praying")
        await asyncio.sleep(10)
        print("I'm done praying")


sample_bot()
