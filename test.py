import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
import pytz
from aiomql import MetaTrader, Symbol, TimeFrame, Account, ForexSymbol


async def main():
    async with Account() as account:
        d = datetime.now()
        start = d.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.timezone('UTC'))
        print(start.timestamp())
        end = d.replace(hour=7, minute=0, second=0, microsecond=0, tzinfo=pytz.timezone('UTC'))
        # print(end.timestamp())
        s = ForexSymbol(name='EURUSD')
        s1 = ForexSymbol(name='USDJPY')
        await s.init()
        await s1.init()
        # t = await s.copy_ticks_range(date_from=start, date_to=end)
        # t1 = await s1.copy_ticks_range(date_from=start, date_to=end)
        r = await s1.copy_rates_range(date_from=start, date_to=end, timeframe=TimeFrame.M1)
        # rc = await s1.copy_rates_from(date_from=end, timeframe=TimeFrame.M15, count=96)
        print(datetime.fromtimestamp(r[0].time, tz=pytz.timezone('UTC')), datetime.fromtimestamp(r[-1].time), len(r))
        # f = await s.copy_ticks_range(date_from=start, date_to=end)
        # print(datetime.fromtimestamp(f[0].time), datetime.fromtimestamp(f[-1].time), len(f))
        # print(len(f), len(rc), rc[50].open)
        # print(len(r), r[-1].time, len(rc), rc[-1].time - rc[-2].time, end.timestamp(),rc[0].time)

asyncio.run(main())
