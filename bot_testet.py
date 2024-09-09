import asyncio

from aiomql import MetaTester, StrategyTester, FingerTrapTest, ForexSymbol, Account, TestData, GetData, Config, \
    TestStrategy, EventManager


async def st_testr():
    config = Config()
    da = GetData.load_data(name=f"{config.test_data_dir}/01-08-24_31-08-24")
    # print(da)
    td = TestData(da)
    st1 = FingerTrapTest(symbol=ForexSymbol(name='Volatility 100 (1s) Index'))
    st2 = FingerTrapTest(symbol=ForexSymbol(name='Volatility 25 Index'))
    st = StrategyTester(strategies=[st1, st2], test_data=td)
    await st.run()


async def st_one():
    sym = ForexSymbol(name='Volatility 100 (1s) Index')
    st1 = FingerTrapTest(symbol=sym)
    config = Config()
    da = GetData.load_data(name=f"{config.test_data_dir}/01-08-24_31-08-24")
    config.test_data = TestData(da)
    st1.set_up()
    await sym.init()
    await st1.test_single()


asyncio.run(st_testr())
