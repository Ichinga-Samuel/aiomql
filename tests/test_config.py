from aiomql import config

from . import get_config, get_default_config


def test_default_config_file(get_default_config):
    conf = config.Config()
    assert conf.win_percentage == 0.90


def test_config_file_name(get_config):
    conf = config.Config(filename='config.json')
    assert conf.win_percentage == 0.8
