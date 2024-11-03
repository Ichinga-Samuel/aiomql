from aiomql.core.config import Config
from aiomql.core.backtesting import BackTestEngine


class TestConfig:
    def test_singleton(self, config):
        config2 = Config(filename="test.json")
        assert config is config2

    def test_set_attributes(self, config):
        config.set_attributes(timeout=5000, record_trades=False)
        assert config.timeout == 5000
        assert config.record_trades is False

    def test_backtest_engine(self, config):
        engine = BackTestEngine()
        config.backtest_engine = engine
        assert config.backtest_engine is engine

    def test_account_info(self, config):
        account_info = config.account_info()
        assert isinstance(account_info, dict)
        assert "login" in account_info
        assert "password" in account_info
        assert "server" in account_info

    def test_load_config(self, config):
        config.load_config(file="tests/live/configs/test2.json")
        assert config.filename == "test2.json"
