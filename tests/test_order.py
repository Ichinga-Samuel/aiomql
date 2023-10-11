# import asyncio
# from pprint import pprint as pp
# from aiomql import Order, Account, ForexSymbol, RAM, OrderType
#
#
# async def test_send_order():
#     await Account().sign_in()
#     symbol = ForexSymbol(name='Volatility 50 Index')
#     await symbol.init()
#     tick = await symbol.info_tick()
#     pips = 100
#     volume = await symbol.compute_volume(amount=100, pips=pips)
#     sls = symbol.trade_stops_level
#     cls = pips * symbol.pip
#     print(sls, cls)
#     sl = tick.ask - (cls)
#     tp = tick.ask + (cls)
#     sls = symbol.trade_stops_level
#     po = sls * symbol.point
#     pi = po * 10
#     # print(sls, po, pi, sl)
#     print(volume)
#     order = Order(symbol=symbol.name, type=OrderType.BUY, sl=sl, tp=tp, volume=volume, price=tick.ask)
#     res = await order.send()
#     pp(res.dict)

asyncio.run(test_send_order())

