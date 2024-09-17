import asyncio

from aiomql import MetaTester, StrategyTester, FingerTrapTest, ForexSymbol, Account, TestData, GetData, Config, \
    TestStrategy, EventManager, FingerTrapSingleTest, SingleStrategyTester


async def test_mul():
    config = Config()
    name = config.test_data_dir/"august_2024.pkl"
    data = GetData.load_data(name=name)
    td = TestData(data)
    st1 = FingerTrapTest(symbol=ForexSymbol(name='Volatility 100 (1s) Index'))
    st2 = FingerTrapTest(symbol=ForexSymbol(name='Volatility 25 Index'))
    st = StrategyTester(strategies=[st1, st2])
    await st.run(td)


async def test_one():
    sym = ForexSymbol(name='Volatility 100 (1s) Index')
    st1 = FingerTrapSingleTest(symbol=sym)
    config = Config()
    data = GetData.load_data(name=f"{config.test_data_dir}/august_24.pkl")
    td = TestData(data)
    st = SingleStrategyTester(strategy=st1)
    await st.run(td)


asyncio.run(test_mul())
