from dataclasses import dataclass, field
from typing import ClassVar
from logging import getLogger

from ...lib import Symbol, Positions, Order
from ...core.models import TradePosition, TradeAction, OrderSendResult
from ...core.constants import OrderType
from ...core.config import Config
from .position_tracker import PositionTracker

logger = getLogger()


@dataclass
class OpenPosition:
    symbol: Symbol
    ticket: int
    position: TradePosition
    is_open: bool = True
    trackers: list[PositionTracker] = field(default_factory=list)
    use_checkpoint: bool = False
    checkpoint: float = 0
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

    async def remove_closed(self):
        try:
            await self.update_position()
            if not self.is_open:
                self.remove_from_state()
        except Exception as exe:
            logger.error("%s: Unable to remove closed position from state", exe)


    def add_tracker(self, *, tracker: PositionTracker, number: int = None):
        number = number or len(self.trackers)
        tracker.set_position(self, number)
        self.trackers.append(tracker)
        self.trackers.sort(key=lambda x: x.number)

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

    async def track(self):
        try:
            for tracker in self.trackers:
                await tracker()
        except Exception as exe:
            logger.error("%s: Error occurred in track method of Open Position for %d:%s",
                         exe, self.symbol.name, self.ticket)


    async def hedge_position(self, *, hedge_params: dict = None) -> tuple[bool, OrderSendResult | None]:
        try:
            # hedge_params for customizing the hedge
            hedge_params = hedge_params or {}
            volume = hedge_params.get("volume", self.position.volume)
            order_type = hedge_params.get("type") or OrderType(self.position.type).opposite
            tick = await self.symbol.info_tick()
            price = hedge_params.get("price") or (tick.ask if order_type == OrderType.BUY else tick.bid)
            comment = hedge_params.get("comment", f"Hedge_{self.ticket}")
            hedge_order = Order(type=order_type, symbol=self.symbol.name, volume=volume, price=price, comment=comment)

            # if position has stops get them from the sl and tp of the position
            if self.position.sl and self.position.tp:
                osl = abs(self.position.sl - self.position.price_open)
                otp = abs(self.position.tp - self.position.price_open)
                if order_type == OrderType.BUY:
                    sl = hedge_params.get("sl") or tick.ask - osl
                    tp = hedge_params.get("tp") or tick.ask + otp
                    hedge_order.set_attributes(tp=tp, sl=sl)
                if order_type == OrderType.SELL:
                    sl = hedge_params.get("sl") or tick.bid + osl
                    tp = hedge_params.get("sl") or tick.bid - otp
                    hedge_order.set_attributes(tp=tp, sl=sl)

            res = await hedge_order.send()
            if res.retcode == 10009:
                return True, res
            return False, res
        except Exception as exe:
            logger.error("%s: Error occurred in %s.hedge_position for %s:%d", exe, self.__class__.__name__,
                         self.symbol.name, self.ticket)
            return False, None
