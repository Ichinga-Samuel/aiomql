import asyncio
import logging
from datetime import datetime, UTC

from aiomql.lib.backtest_runner import BackTestRunner
from aiomql.core import Config
from aiomql.contrib.strategies import FingerTrap, Chaos
from aiomql.contrib.symbols import ForexSymbol
from aiomql.contrib.backtesting import BackTestEngine


async def back_tester():
    config = Config()
    config.mode = 'backtest'
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    syms = ['Volatility 75 Index', 'Volatility 100 Index', 'Volatility 50 Index']
    symbols = [ForexSymbol(name=sym) for sym in syms]
    stgs = [Chaos(symbol=symbol) for symbol in symbols]
    start = datetime(2021, 1, 1, tzinfo=UTC)
    end = datetime(2021, 1, 7, tzinfo=UTC)
    back_test_engine = BackTestEngine(start=start, end=end)
    await back_test_engine.setup_account(balance=100)
    back_test_runner = BackTestRunner(strategies=stgs, backtest_engine=back_test_engine)
    await back_test_runner.run()


asyncio.run(back_tester())
print("Bot executed successfully")
