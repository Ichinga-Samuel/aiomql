import logging

import asyncio
from datetime import datetime
from aiomql import ForexSymbol, Account, Positions, History, SimpleTrader as Trader, OrderType, RAM

logging.basicConfig(level=logging.INFO, filemode='w', filename='example.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    # Account details are in the aiomql.json file
    async with Account():

        # get start time
        start = datetime.now()

        # create two symbols and initialize them
        sym1 = ForexSymbol(name="EURUSD-T")
        sym2 = ForexSymbol(name="GBPUSD-T")
        await sym1.init()
        await sym2.init()

        # Risk Assets Management instance
        # fix the amount to be risked at 2 USD. USD is the account currency.
        ram = RAM(amount=2, points=100)

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
        end = datetime.now()

        # get the number of open positions
        total = await pos.positions_total()
        print(f'{total} Open positions')

        # get historical trades
        start = datetime(day=start.day-1, month=start.month, year=start.year, hour=start.hour, minute=0, second=0)
        his = History(date_from=start.timestamp(), date_to=end.timestamp())

        # get the number of order
        orders = await his.orders_total()
        print(f'{orders} orders')

        # get the number of deals
        # total_deals = await his.deals_total()
        # print(f'{total_deals} Deals')


asyncio.run(main())