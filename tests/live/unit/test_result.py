import asyncio

import pytest

from aiomql.lib.result import Result
from aiomql.core.models import OrderSendResult


class TestResult:
    @pytest.fixture(scope="class")
    def parameters(self):
        return {"name": "test_trades", "ema": 20, "rsi": 14}

    @pytest.fixture(scope="function")
    async def order_results(self, mt, sell_order, buy_order, parameters):
        res1 = await mt.order_send(sell_order)
        res2 = await mt.order_send(buy_order)
        res1 = Result(result=OrderSendResult(**res1._asdict()), parameters=parameters)
        res2 = Result(result=OrderSendResult(**res2._asdict()), parameters=parameters)
        return res1, res2

    async def test_get_data(self, order_results):
        res1, res2 = order_results
        data1 = res1.get_data()
        data2 = res2.get_data()
        assert data1["actual_profit"] == data2["actual_profit"] == 0
        assert data1["closed"] == data2["closed"] == False
        assert data1["win"] == data2["win"] == False

    async def test_csv(self, order_results):
        res1, res2 = order_results
        await asyncio.gather(res1.save(), res2.save())
        assert res1.config.records_dir.exists()
        record = res1.config.records_dir / f"{res1.name}.csv"
        assert record.exists()

    async def test_json(self, order_results):
        res1, res2 = order_results
        await asyncio.gather(res1.save(trade_record_mode="json"), res2.save(trade_record_mode="json"))
        assert res1.config.records_dir.exists()
        record = res1.config.records_dir / f"{res1.name}.json"
        assert record.exists()
