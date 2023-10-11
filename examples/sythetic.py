from aiomql import ForexSymbol, Order, Trader, Account
import asyncio


async def main():
    async with Account():
        les = ForexSymbol(name='Volatility 50 (1s) Index')
        # t = ForexSymbol(name='EURUSD')
        await les.init()
        # await t.init()
        await les.info_tick()
        # await t.info_tick()
        vol = await les.compute_volume(amount=50, pips=10)
        print(les.tick.ask, les.tick.bid, les.volume_min, vol, les.point, les.digits, les.volume_max)
        print(les.tick.ask + les.point*100)

asyncio.run(main())