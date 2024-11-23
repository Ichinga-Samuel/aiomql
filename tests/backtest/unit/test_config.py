
def test_config(config, capsys):
    print(config.filename, config.root, config.mode, config.config_file)
    assert 6 == 6
    assert config.mode == "backtest"
