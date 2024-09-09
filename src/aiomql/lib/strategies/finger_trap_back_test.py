from .finger_trap import FingerTrap
from ...contrib.backtester.test_strategy import TestStrategy


class FingerTrapTest(TestStrategy, FingerTrap):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_up()

    async def test(self):
        print(f"Backtesting {self.symbol}")
        while True:
            await self.event_manager.acquire()
            try:
                await self.event_manager.wait()
                await self.watch_market()

                if not self.tracker.new:
                    continue

                if self.tracker.order_type is not None:
                    await self.trader.place_trade(order_type=self.tracker.order_type, parameters=self.parameters,
                                                  sl=self.tracker.sl)
                await self.sleep(self.tracker.snooze)
            except Exception as err:
                print(f"{err} For {self.symbol} in {self.__class__.__name__}.trade")
                await self.sleep(self.ttf.time)

            finally:
                self.event_manager.release()
