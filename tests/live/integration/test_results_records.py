import asyncio
import json
from csv import DictReader

import pytest

from aiomql.lib.result import Result
from aiomql.core.models import OrderSendResult
from aiomql.lib.trade_records import TradeRecords
from aiomql.lib.positions import Positions


class TestRecordsAndResults:
    @classmethod
    def setup_class(cls):
        cls.trade_records = TradeRecords()

    @pytest.fixture(scope="class")
    async def buy(self, mt):
        sym = "BTCUSD"
        sym_info = await mt.symbol_info(sym)
        dsl = (sym_info.trade_stops_level + sym_info.spread) * 2 * sym_info.point
        sl = sym_info.ask - dsl
        tp = sym_info.ask + dsl
        return {
            "action": mt.TRADE_ACTION_DEAL,
            "symbol": sym,
            "volume": sym_info.volume_min,
            "type": mt.ORDER_TYPE_BUY,
            "price": sym_info.ask,
            "sl": sl,
            "tp": tp,
        }

    @pytest.fixture(scope="class")
    async def sell(self, mt):
        sym = "BTCUSD"
        sym_info = await mt.symbol_info(sym)
        return {"action": mt.TRADE_ACTION_DEAL, "symbol": sym, "volume": sym_info.volume_min, "type": mt.ORDER_TYPE_SELL, "price": sym_info.bid}

    @pytest.fixture(scope="class", autouse=True)
    async def setup(self, sell, buy, mt):
        buy_res = await mt.order_send(buy)
        buy_res_2 = await mt.order_send(buy)
        sell_res = await mt.order_send(sell)
        sell_res_2 = await mt.order_send(sell)
        buy_res = Result(result=OrderSendResult(**buy_res._asdict()), name="test_result")
        sell_res = Result(result=OrderSendResult(**sell_res._asdict()), name="test_result")
        sell_res_2 = Result(result=OrderSendResult(**sell_res_2._asdict()), name="test_result")
        buy_res_2 = Result(result=OrderSendResult(**buy_res_2._asdict()), name="test_result")
        await asyncio.gather(buy_res.save(), sell_res.save(), buy_res_2.save(trade_record_mode="json"), sell_res_2.save(trade_record_mode="json"))
        await Positions().close_all()

    def test_records_dir(self):
        records_dir = self.trade_records.records_dir
        assert records_dir.is_dir()
        recs = list(records_dir.iterdir())
        assert len(recs) >= 2
        csvs, jsons = [], []
        matched_recs = list(records_dir.glob("test_result.*"))
        assert len(matched_recs) == 2
        for rec in matched_recs:
            if rec.match("test_result.json"):
                jsons.append(rec)
            elif rec.match("test_result.csv"):
                csvs.append(rec)
            else:
                continue
        assert len(csvs) == 1
        assert len(jsons) == 1

    async def test_json_records(self):
        json_records = self.trade_records.get_json_records()
        matched_recs = [record for record in json_records if record.match("test_result.json")]
        assert len(matched_recs) == 1
        record = matched_recs[0]
        record_data = json.load(record.open())
        assert isinstance(record_data, list)
        assert len(record_data) == 2
        is_open = [data["closed"] is False for data in record_data]
        assert all(is_open)
        await self.trade_records.update_json_records()
        is_close = [data["closed"] is True for data in record_data]
        assert len(is_close) == 2

    async def test_csv_records(self):
        csv_records = self.trade_records.get_csv_records()
        matched_recs = [record for record in csv_records if record.match("test_result.csv")]
        assert len(matched_recs) == 1
        record = matched_recs[0]
        record_data = DictReader(record.open())
        record_data = [row for row in record_data]
        assert isinstance(record_data, list)
        assert len(record_data) == 2
        is_open = [data["closed"].title() == "False" for data in record_data]
        assert all(is_open)
        await self.trade_records.update_json_records()
        is_close = [data["closed"].title() == "True" for data in record_data]
        assert len(is_close) == 2
