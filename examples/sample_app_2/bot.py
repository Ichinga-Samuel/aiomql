import asyncio

from aiomql import Bot, ForexSymbol

from .strategies.ribbon_scalper import RibbonScalper

async def rs_bot():
    bot = Bot()
    syms = ["ETHUSD", "BTCUSD", "ADAUSD", "SOLUSD", "LTCUSD", "XRPUSD"]
    strategies = [RibbonScalper(symbol=ForexSymbol(name=sym)) for sym in syms]
    bot.add_strategies(strategies=strategies)
    await bot.start()


if __name__ == "__main__":
    asyncio.run(rs_bot())
