import asyncio
from datetime import datetime
from aiomql import ForexSymbol, Account, Positions, History, Trader, OrderType, RAM


async def main():
    # Account details are in the aiomql.json file
    async with Account():

        # get start time using local timezone
        tz = datetime.now().astimezone().tzinfo
        start = datetime.now(tz=tz)

        # create two symbols and initialize them
        sym1 = ForexSymbol(name="EURUSD")
        sym2 = ForexSymbol(name="GBPUSD")
        await sym1.init()
        await sym2.init()

        # Risk Assets Management instance
        # fix the amount to be risked at 2 USD. USD is the account currency.
        ram = RAM(amount=2)

        # Create two traders instance
        trd = Trader(symbol=sym1, ram=ram)
        trd2 = Trader(symbol=sym2, ram=ram)

        # Place Trades
        await trd.place_trade(order_type=OrderType.SELL)
        await trd2.place_trade(order_type=OrderType.BUY)

        # Create a Positions object
        pos = Positions(group='*USD*')

        # get the number of open positions
        total = await pos.positions_total()
        print(f'{total} Open positions') # 2

        # close all open positions
        await pos.close_all()
        end = datetime.now(tz=tz)

        # get the number of open positions
        total = await pos.positions_total()
        print(f'{total} Open positions') # 0

        # get historical trades
        his = History(date_from=start, date_to=end)

        # get the number of deals
        total_deals = await his.deals_total()
        print(f'{total_deals} Deals')

        # get the number of order
        orders = await his.orders_total()
        print(f'{orders} orders')


asyncio.run(main())
