from datetime import datetime, timedelta

import pytest

from aiomql.lib.symbol import Symbol
from aiomql.lib.candle import Candles
from aiomql.lib.ticks import Ticks


class TestSymbol:
    @pytest.fixture(scope="class", autouse=True)
    async def btc(self):
        symbol = Symbol(name="BTCUSD")
        select = getattr(symbol, "select", False)
        if select is False:
            await symbol.initialize()
        return symbol

    async def test_symbol_attributes(self, btc):
        assert btc.name == "BTCUSD"
        assert btc.select is True
        assert btc.tick is not None

    async def test_volume(self, btc):
        volume = btc.volume_min - btc.volume_step
        success, volume = btc.check_volume(volume=volume)
        assert success is False
        volume = btc.volume_min + btc.volume_step * 2
        success, volume = btc.check_volume(volume=volume)
        assert success is True
        volume = btc.volume_min + btc.volume_step * 2.5
        volume = btc.round_off_volume(volume=volume, round_down=True)
        assert volume == btc.volume_min + btc.volume_step * 2

    async def test_rates(self, btc):
        start = datetime(year=2023, month=10, day=5)
        end = start + timedelta(hours=9)
        rates_from = await btc.copy_rates_from(
            timeframe=btc.mt5.TIMEFRAME_H1, date_from=start, count=10
        )
        assert isinstance(rates_from, Candles)
        assert len(rates_from) == 10
        rates_from_pos = await btc.copy_rates_from_pos(
            timeframe=btc.mt5.TIMEFRAME_H1, count=10, start_position=0
        )
        assert isinstance(rates_from_pos, Candles)
        assert len(rates_from_pos) == 10
        rates_range = await btc.copy_rates_range(
            timeframe=btc.mt5.TIMEFRAME_H1, date_from=start, date_to=end
        )
        assert isinstance(rates_range, Candles)
        assert len(rates_range) == 10
        ticks_from = await btc.copy_ticks_from(date_from=start, count=10)
        assert isinstance(ticks_from, Ticks)
        assert len(ticks_from) == 10
        end = start + timedelta(seconds=20)
        ticks_from_pos = await btc.copy_ticks_range(date_from=start, date_to=end)
        assert isinstance(ticks_from_pos, Ticks)
        assert len(ticks_from_pos) >= 10
