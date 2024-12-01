import logging
from datetime import datetime, UTC

from aiomql.lib.backtester import BackTester
from aiomql.core import Config
from aiomql.contrib.strategies import FingerTrap, Chaos
from aiomql.contrib.symbols import ForexSymbol
from aiomql.core.backtesting import BackTestEngine


def back_tester():
    Config(mode="backtest")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    syms = ["Volatility 75 Index", "Volatility 100 Index", "Volatility 25 Index", "Volatility 10 Index"]
    symbols = [ForexSymbol(name=sym) for sym in syms]
    strategies = [FingerTrap(symbol=symbol) for symbol in symbols]
    start = datetime(2024, 5, 1, tzinfo=UTC)
    stop_time = datetime(2024, 5, 2, tzinfo=UTC)
    end = datetime(2024, 5, 7, tzinfo=UTC)
    back_test_engine = BackTestEngine(start=start, end=end, speed=7200,
                                      close_open_positions_on_exit=True, assign_to_config=True, preload=True,
                                      account_info={"balance": 350})
    backtester = BackTester(backtest_engine=back_test_engine)
    backtester.add_strategies(strategies=strategies)
    backtester.execute()


back_tester()
