from aiomql import TradeAction


class TestConstants:

    def test_trade_action(self):
        assert TradeAction.DEAL == 1
