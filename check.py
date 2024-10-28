import asyncio
from datetime import datetime, UTC

from aiomql.contrib.backtesting.get_data import BackTestData, GetData
from aiomql.contrib.backtesting.backtest_engine import BackTestEngine
from aiomql.core.constants import TimeFrame
from aiomql.core.meta_trader import MetaTrader


async def get_data():
    mt = MetaTrader()
    await mt.login()
    start = datetime(2024, 2, 1, tzinfo=UTC)
    end = datetime(2024, 2, 3, tzinfo=UTC)
    symbols = ['BTCUSD', "ETHUSD", "SOLUSD"]
    timeframes = [TimeFrame.H1, TimeFrame.H2, TimeFrame.M5]
    g_data = GetData(start=start, end=end, symbols=symbols, timeframes=timeframes,
                     name='test_data')
    s = datetime.now().timestamp()
    await g_data.get_data(workers=500)
    e = datetime.now().timestamp()
    print(e - s, 'for getting data')

    s = datetime.now().timestamp()
    g_data.save_data()
    e = datetime.now().timestamp()
    print(e - s, 'for saving data')


async def test_data():
    start = datetime.now().timestamp()
    td = GetData.load_data(name='backtesting/test_data.pkl')
    end = datetime.now().timestamp()
    print(end-start, 'seconds')
    print(td.name)
    print(td.version)
    print(len(td.ticks.keys()))
    print(len(td.symbols.keys()))
    print(td.rates.keys())

async def back_test_engine():
    td = GetData.load_data(name='backtesting/test_data.pkl')
    bt = BackTestEngine(name='test_data_2', start=datetime(2024, 2, 1),
                        end=datetime(2024, 2, 7))
    # bt.next()
    bt.next()
    # print(bt.cursor)
    # now = bt.cursor.time
    # r = bt.cursor.index
    # bt.fast_forward(steps=20)
    # print(bt.cursor.time == now + 20)
    # print(bt.cursor.index == r + 20)
    # print(bt.cursor, r)
    # print(bt.cursor)
    print(bt.range, bt.span)
    bt.go_to(time=datetime(2024, 2, 13))
    print(bt.cursor)
    print(datetime.fromtimestamp(bt.cursor.time))
    print(bt.range, bt.span)


asyncio.run(get_data())
