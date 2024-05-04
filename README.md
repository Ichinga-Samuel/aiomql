# Aiomql - Bot Building Framework and Asynchronous MetaTrader5 Library
![GitHub](https://img.shields.io/github/license/ichinga-samuel/aiomql?style=plastic)
![GitHub issues](https://img.shields.io/github/issues/ichinga-samuel/aiomql?style=plastic)
![PyPI](https://img.shields.io/pypi/v/aiomql)

### Installation
```bash
pip install aiomql
```

### Key Features
- Asynchronous Python Library For MetaTrader5
- Asynchronous Bot Building Framework
- Build bots for trading in different financial markets using a bot factory
- Use threadpool executors to run multiple strategies on multiple instruments concurrently
- Records and keep track of trades and strategies in csv files.
- Helper classes for Bot Building. Easy to use and extend.
- Compatible with pandas-ta.
- Sample Pre-Built strategies
- Visualization of charts using matplotlib and mplfinance
- Manage Trading periods using Sessions
- Risk Management
- Run multiple bots concurrently with different accounts from the same broker or different brokers

### As an asynchronous MetaTrader5 Libray
```python
import asyncio

from aiomql import MetaTrader


async def main():
    mt5 = MetaTrader()
    await mt5.initialize()
    await mt5.login(123456, '*******', 'Broker-Server')
    symbols = await mt5.symbols_get()
    print(symbols)
    
asyncio.run(main())
```

### As a Bot Building FrameWork using a Sample Strategy
***The following code is a sample bot that uses the FingerTrap strategy from the library.\
It assumes that you have a config file in the same directory as the script.\
The config file should be named aiomql.json and should contain the login details for your account.\
It demonstrates the use of sessions and risk management.\
Sessions allows you to specify the trading period for a strategy. You can also set an action to be performed at the end of a session.\
Risk Management allows you to manage the risk of a strategy. You can set the risk per trade and the risk to reward ratio.\
The trader class handles the placing of orders and risk management. It is an attribute of the strategy class.***

```python
from datetime import time
import logging

from aiomql import Bot, ForexSymbol, FingerTrap, Session, Sessions, RAM, SimpleTrader, TimeFrame

logging.basicConfig(level=logging.INFO)


def build_bot():
    bot = Bot()
    
    # create sessions for the strategies
    london = Session(name='London', start=8, end=time(hour=15, minute=30), on_end='close_all')
    new_york = Session(name='New York', start=13, end=time(hour=20, minute=30))
    tokyo = Session(name='Tokyo', start=23, end=time(hour=6, minute=30))
    
    # configure the parameters and the trader for a strategy
    params = {'trend_candles_count': 500, 'fast_period': 8, 'slow_period': 34, 'etf': TimeFrame.M5}
    gbpusd = ForexSymbol(name='GBPUSD')
    st1 = FingerTrap(symbol=gbpusd, params=params, trader=SimpleTrader(symbol=gbpusd, ram=RAM(risk=0.05, risk_to_reward=2)),
                     sessions=Sessions(london, new_york))
    
    # use the default for the other strategies
    st2 = FingerTrap(symbol=ForexSymbol(name='AUDUSD'), sessions=Sessions(tokyo, new_york))
    st3 = FingerTrap(symbol=ForexSymbol(name='USDCAD'), sessions=Sessions(new_york))
    st4 = FingerTrap(symbol=ForexSymbol(name='USDJPY'), sessions=Sessions(tokyo))
    st5 = FingerTrap(symbol=ForexSymbol(name='EURGBP'), sessions=Sessions(london))
    
    # sessions are not required
    st6 = FingerTrap(symbol=ForexSymbol(name='EURUSD'))
    
    # add strategies to the bot
    bot.add_strategies([st1, st2, st3, st4, st5, st6])
    bot.execute()

# run the bot
build_bot()
```
## API Documentation
see [API Documentation](https://github.com/Ichinga-Samuel/aiomql/tree/master/docs) for more details

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Support
Feeling generous, like the package or want to see it become a more mature package?

Consider supporting the project by buying me a coffee.\
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/ichingasamuel)
