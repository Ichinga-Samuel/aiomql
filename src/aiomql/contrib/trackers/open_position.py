from dataclasses import dataclass, field
from typing import ClassVar, Self
from logging import getLogger

from ...lib import Symbol, Positions, Order
from ...core.models import TradePosition, TradeAction, OrderSendResult
from ...core.constants import OrderType
from ...core.config import Config
from ..quants import percentage_increase, percentage_decrease
from .position_tracker import PositionTracker

logger = getLogger()


@dataclass
class OpenPosition:
    symbol: Symbol
    ticket: int
    position: TradePosition
    is_open: bool = True
    use_checkpoint: bool = False
    checkpoint: float = None
    is_hedged: bool = False
    is_a_hedge: bool = False
    hedge: Self | None = None
    pending_hedge: OrderSendResult | None = None
    _trackers: dict[str, PositionTracker] = field(default_factory=dict)
    positions: ClassVar[Positions]
    state_key: ClassVar[str] = "tracked_positions"
    config: ClassVar[Config]

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "config"):
            cls.config = Config()
        if not hasattr(cls, "positions"):
            cls.positions = Positions()
        return super().__new__(cls)

    def __post_init__(self):
        self.config.state.setdefault(self.state_key, {}).setdefault(self.ticket, self)

    def add_tracker(self, *, tracker: PositionTracker, number: int = None, name: str = ""):
        number = number or len(self._trackers) + 1
        tracker.set_position(self, number)
        self._trackers[name or tracker.function.__name__] = tracker

    @property
    def trackers(self):
        for tracker in sorted(self._trackers, key=lambda key: self._trackers[key].number):
            yield self._trackers[tracker]

    async def remove_closed(self):
        try:
            await self.update_position()
            if not self.is_open:
                self.remove_from_state()
        except Exception as exe:
            logger.error("%s: Unable to remove closed position from state", exe)

    async def update_position(self) -> bool:
        pos = await self.positions.get_position_by_ticket(ticket=self.ticket)
        if pos is not None:
            self.position = pos
            self.is_open = True
        else:
            self.is_open = False
        return self.is_open

    async def modify_stops(self, *, sl: float = None, tp: float = None,
                           use_stop_levels=False) -> tuple[bool, OrderSendResult | None]:
        try:
            tick = await self.symbol.info_tick()

            # modify stop_loss
            if sl is not None and use_stop_levels is True:
                min_stops_value = (self.symbol.trade_stops_level + self.symbol.spread) * self.symbol.point
                if self.position.type == OrderType.BUY:
                    sl = min(sl, tick.ask - min_stops_value)
                elif self.position.type == OrderType.SELL:
                    sl = max(sl, tick.bid + min_stops_value)
                else:
                    raise TypeError("Invalid OrderType %s: In %s.modify_stops", self.position.type, self.__class__.__name__)
            elif sl is not None and use_stop_levels is False:
                sl = sl or self.position.sl

            # modify take_profit
            if tp is not None and use_stop_levels is True:
                min_stops_value = (self.symbol.trade_stops_level + self.symbol.spread) * self.symbol.point
                if self.position.type == OrderType.BUY:
                    tp = max(tp, tick.ask + min_stops_value)
                elif self.position.type == OrderType.SELL:
                    tp = min(tp, tick.bid - min_stops_value)
                else:
                    raise TypeError("Invalid OrderType %s: In %s.modify_stops", self.position.type, self.__class__.__name__)
            elif tp is not None and use_stop_levels is False:
                tp = tp or self.position.tp

            # send order
            order = Order(position=self.ticket, sl=sl, tp=tp, action=TradeAction.SLTP)
            res = await order.send()
            if res and res.retcode == 10009:
                await self.update_position()
                return True, res
            else:
                return False, res
        except Exception as exe:
            logger.error("%s: Error occurred in %s.modify_stops for %s:%d",
                         exe, self.__class__.__name__, self.symbol.name, self.ticket)
            return False, None

    def remove_from_state(self):
        try:
            self.config.state.get(self.state_key, {}).pop(self.ticket, None)
        except KeyError as err:
            logger.error("%s: Unable to remove closed position from state in", err)

    async def close_position(self, remove_from_state: bool = True) -> tuple[bool, OrderSendResult | None]:
        try:
            res = await self.positions.close_position(position=self.position)
            if res.retcode == 10009:
                self.is_open = False
                if remove_from_state:
                    self.remove_from_state()
                return True, res
            else:
                return False, res
        except Exception as exe:
            logger.error("%s: Error occurred in %s.close_position for %s:%d", exe, self.__class__.__name__,
                         self.symbol.name, self.ticket)
            return False, None

    @staticmethod
    async def check_pending_order(self):
        await self.update_position()
        if self.is_open and self.is_hedged and self.pending_hedge is not None:
            pos = await self.positions.get_position_by_ticket(ticket=self.pending_hedge.order)
            if pos is not None:
                self.pending_hedge = None
                self.hedge = OpenPosition(symbol=self.symbol, position=pos, ticket=pos.ticket,
                                          is_a_hedge=True, hedge=self)

    async def track(self):
        try:
            for tracker in self.trackers:
                await tracker()
        except Exception as exe:
            logger.error("%s: Error occurred in track method of Open Position for %d:%s",
                         exe, self.symbol.name, self.ticket)

    async def get_price_from_profit(self, profit):
        action = OrderType.BUY if self.position.type == 0 else OrderType.SELL
        volume = self.position.volume
        price_open = self.position.price_open
        price_close = percentage_increase(price_open, 50) if action == 0 else percentage_decrease(price_open, 50)
        half_profit = await Order.mt5.order_calc_profit(symbol=self.symbol.name, action=action, volume=volume,
                                             price_open=price_open, price_close=price_close)
        rate = profit / half_profit * 50
        rate = percentage_increase(price_open, rate) if action == 0 else percentage_decrease(price_open, rate)
        return rate

    async def hedge_order(self, price, **order_params) -> tuple[bool, OrderSendResult | None]:
        try:
            order_type = OrderType.SELL_STOP if self.position.type == OrderType.BUY else OrderType.BUY_STOP
            volume = order_params.get("volume", self.position.volume)
            order = Order(action=TradeAction.PENDING, symbol=self.symbol.name, type=order_type, price=price, volume=volume)
            res = await order.send()
            if res.retcode != 10009:
                return False, res
            self.pending_hedge = res
            self.is_hedged = True
            self.add_tracker(tracker=PositionTracker(self.check_pending_order), number=0, name="check_pending_order")
            return True, res
        except Exception as exe:
            logger.error("%s: Error occurred in hedge_order method of Open Position for %d:%s", exe, self.symbol.name, self.ticket)
            return False, None

    async def hedge_position(self, *, hedge_params: dict = None) -> tuple[bool, Self]:
        try:
            # hedge_params for customizing the hedge
            hedge_params = hedge_params or {}
            volume = hedge_params.get("volume", self.position.volume)
            order_type = hedge_params.get("type") or OrderType(self.position.type).opposite
            if (price := hedge_params.get("price", None)) is None:
                tick = await self.symbol.info_tick()
                price = (tick.ask if order_type == OrderType.BUY else tick.bid)
            comment = hedge_params.get("comment", f"Hedge_{self.ticket}")
            hedge_order = Order(type=order_type, symbol=self.symbol.name, volume=volume, price=price, comment=comment)
            res = await hedge_order.send()
            if res.retcode != 10009:
                return False, None
            self.is_hedged = True
            hedge_pos = await self.positions.get_position_by_ticket(ticket=res.order)
            self.hedge = OpenPosition(symbol=self.symbol, ticket=res.order, position=hedge_pos,
                                      hedge=self, is_a_hedge=True)
            return True, self.hedge
        except Exception as exe:
            logger.error("%s: Error occurred in %s.hedge_position for %s:%d", exe, self.__class__.__name__,
                         self.symbol.name, self.ticket)
            return False, None
