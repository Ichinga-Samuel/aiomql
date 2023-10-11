import asyncio

from aiomql import Account, OrderType, TradeAction, Order, ForexSymbol


async def main():
    async with Account():

        # create a symbol
        sym = ForexSymbol(name="EURUSD")

        # Confirm the symbol is available for this account and initialize with default values.
        res = await sym.init()

        # I want to place a market buy order, risk only 2usd, and target 10 pips in this trade.
        # The ForexSymbol object has a compute_volume method that can be used to compute the volume
        # given a target pips and amount.
        volume = await sym.compute_volume(amount=2, pips=10)

        # a risk to reward ratio of 1:2
        # get the price tick of the symbol
        tick = await sym.info_tick()
        sl = tick.ask - (10 * sym.pip)
        tp = tick.ask + (20 * sym.pip)
        # create order
        order = Order(symbol=sym.name, type=OrderType.BUY, volume=volume, action=TradeAction.DEAL,
                      price=tick.ask, sl=sl, tp=tp)
        # check order. returns an OrderCheckResult object
        chk = await order.check()
        print(chk)

        # send order returns an OrderSendResult object
        res = await order.send()
        print(res)


asyncio.run(main())
