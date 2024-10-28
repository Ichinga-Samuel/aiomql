from datetime import datetime

from aiomql.lib.ticks import Ticks, Tick
from pandas import Series

class TestTicks:
    async def test_tick(self, mt):
        btc_tick = await mt.symbol_info_tick("BTCUSD")
        btc_tick = Tick(**btc_tick._asdict())
        tick_dict = btc_tick.dict(include={'ask', 'bid', 'time', 'volume'})
        assert isinstance(btc_tick, Tick)
        assert isinstance(tick_dict, dict)
        assert 'ask' in tick_dict
        assert 'bid' in tick_dict
        assert 'volume_real' not in tick_dict

    async def test_ticks(self, mt):
        start = datetime(year=2023, month=10, day=5)
        ticks = await mt.copy_ticks_from("BTCUSD", start, 10, mt.COPY_TICKS_ALL)
        ticks = Ticks(data=ticks)
        assert isinstance(ticks, Ticks)
        assert len(ticks) == 10
        assert isinstance(ticks[0], Tick)
        bids = ticks['bid']
        assert len(bids) == 10
        assert isinstance(bids, Series)
