"""Open position management with tracking, hedging, and stacking capabilities.

This module provides classes for managing open trading positions, including
support for hedging, stacking, pending orders, and custom tracking functions.

Classes:
    PendingOrder: Represents a pending order associated with an open position.
    OpenPosition: Manages an open trading position with full tracking capabilities.
"""
from dataclasses import dataclass, field
from typing import ClassVar, Self
from logging import getLogger
import asyncio

from ...lib import Symbol, Positions, Order
from ...core.models import TradePosition, TradeAction, OrderSendResult
from ...core.constants import OrderType
from ...core.config import Config
from ...utils.price_utils import increase_value_by_pct, decrease_value_by_pct
from .position_trackers import PositionTracker

logger = getLogger()


@dataclass
class PendingOrder:
    """Represents a pending order associated with an open position.
    
    Pending orders can be hedges (opposite direction) or stacks (same direction)
    that are placed but not yet filled.
    
    Attributes:
        order: The OrderSendResult containing order details and status.
        is_hedge: True if this is a hedging order (opposite direction).
        is_stack: True if this is a stacking order (same direction).
        open_pos_params: Additional parameters to apply when creating the
            OpenPosition once the pending order is filled.
    """
    order: OrderSendResult
    is_hedge: bool = False
    is_stack: bool = False
    open_pos_params: dict = field(default_factory=dict)


@dataclass
class OpenPosition:
    """Manages an open trading position with tracking, hedging, and stacking.
    
    Provides comprehensive position management including stop loss/take profit
    modification, position closing, hedging (opening opposite positions), and
    stacking (adding to existing positions). Supports custom tracking functions
    via the PositionTracker system.
    
    Attributes:
        symbol: The Symbol instance for this position's trading instrument.
        ticket: Unique ticket number identifying this position.
        position: The TradePosition model with current position data.
        is_open: Whether the position is currently open.
        is_hedged: Whether this position has active hedge positions.
        is_stacked: Whether this position has active stack positions.
        is_a_stack: Whether this position is itself a stack of another position.
        is_a_hedge: Whether this position is itself a hedge of another position.
        hedge: Reference to the parent position if this is a hedge.
        stack: Reference to the parent position if this is a stack.
        pending_orders: Dictionary of pending orders keyed by order ticket.
        hedges: Dictionary of hedge positions keyed by ticket.
        stacks: Dictionary of stack positions keyed by ticket.
        close_pending_orders_on_close: Cancel pending orders when position closes.
        remove_from_state_on_close: Remove from state tracking when closed.
        auto_track_closed: Automatically add tracker for detecting closed positions.
        close_hedges_on_close: Close all hedge positions when this closes.
        close_stacks_on_close: Close all stack positions when this closes.
        positions: Class-level Positions handler shared by all instances.
        state_key: Key for storing tracked positions in state.
        archive_key: Key for storing archived (closed) positions in state.
        config: Class-level configuration shared by all instances.
    """
    symbol: Symbol
    ticket: int
    position: TradePosition
    is_open: bool = True
    is_hedged: bool = False
    is_stacked: bool = False
    is_a_stack: bool = False
    is_a_hedge: bool = False
    hedge: Self | None = None
    stack: Self | None = None
    pending_orders: dict[int, PendingOrder] = field(default_factory=dict)
    hedges: dict[int, "OpenPosition"] = field(default_factory=dict)
    stacks: dict[int, "OpenPosition"] = field(default_factory=dict)
    close_pending_orders_on_close: bool = True
    remove_from_state_on_close: bool = True
    auto_track_closed: bool = True
    close_hedges_on_close: bool = False
    close_stacks_on_close: bool = False
    _trackers: dict[str, PositionTracker] = field(default_factory=dict)
    positions: ClassVar[Positions]
    state_key: ClassVar[str] = "tracked_positions"
    archive_key: ClassVar[str] = "archived_positions"
    config: ClassVar[Config]

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "config"):
            cls.config = Config()
        if not hasattr(cls, "positions"):
            cls.positions = Positions()
        return super().__new__(cls)

    def __post_init__(self):
        self.config.state.setdefault(self.state_key, {}).setdefault(self.ticket, self)
        if self.auto_track_closed:
            PositionTracker(self, self.remove_closed, name="remove_closed_tracker", rank=1)
        PositionTracker(self, self.check_pending_orders, name="pending_orders_tracker", rank=2)

    def add_tracker(self, *, tracker: PositionTracker, name: str = None, rank: int = None):
        """Add a tracker to this position.
        
        Args:
            tracker: The PositionTracker instance to add.
            name: Name identifier for the tracker. Defaults to tracker's name.
            rank: Execution priority (lower executes first). Defaults to
                tracker's rank or next available rank.
        """
        tracker.rank = rank if rank is not None else (tracker.rank if tracker.rank is not None else len(self._trackers) + 1)
        self._trackers[name] = tracker

    @property
    def trackers(self):
        """Yield all trackers in execution order (by rank).
        
        Yields:
            PositionTracker: Each tracker in order of ascending rank.
        """
        for tracker in sorted(self._trackers, key=lambda key: self._trackers[key].rank):
            yield self._trackers[tracker]

    @staticmethod
    async def remove_closed(self, /):
        """
        A static method to remove all closed positions, it accepts an instance of this class.
        Handle position closure cleanup.
        
        Checks if the position is closed and performs cleanup operations
        including closing pending orders, hedges, stacks, and removing
        from state tracking. This is typically used as an automatic tracker.
        """
        try:
            await self.update_position()
            if self.is_open:
                return
            if self.close_pending_orders_on_close:
                await self.close_pending_orders()
            if self.close_hedges_on_close:
                await self.close_hedges()
            if self.close_stacks_on_close:
                await self.close_stacks()
            if self.remove_from_state_on_close:
                self.remove_from_state()
        except Exception as exe:
            logger.error("%s: Error occurred while removing closed position from state", exe)
    
    async def close_pending_orders(self) -> tuple[tuple[bool, PendingOrder], ...]:
        """Close all pending orders associated with this position.
        
        Returns:
            Tuple of (success, PendingOrder) tuples for each order, or None
            if an error occurred. Exceptions during individual cancellations
            are filtered out.
        """
        try:
            pending_orders: list[PendingOrder] = list(self.pending_orders.values())
            ord_res = await asyncio.gather(*[self.close_pending_order(pending_order=pending_order)
             for pending_order in pending_orders], return_exceptions=True)
            return tuple(res for res in ord_res if isinstance(res, tuple) and res[0] is True)
        except Exception as exe:
            logger.error("%s: Error occurred while closing pending orders for %s:%d in %s.close_pending_orders",
             exe, self.symbol.name, self.ticket, self.__class__.__name__)
            return ()

    async def close_pending_order(self, *, pending_order: PendingOrder) -> tuple[bool, PendingOrder]:
        """Cancel a specific pending order.
        
        Args:
            pending_order: The PendingOrder to cancel.
            
        Returns:
            Tuple of (success, updated PendingOrder) or (False, None) on error.
        """
        pending_order_ticket = pending_order.order.order
        res = await Order.cancel_order(order=pending_order_ticket, symbol=pending_order.order.request.symbol)
        if res.retcode != 10009:
            cpo = await Order.get_history_order_by_ticket(ticket=pending_order_ticket) # check if order has been deleted already
            res.comment = f"{res.comment}: Order already canceled)"
            if cpo is None:
                logger.critical("%s: Unable to cancel pending order %d for %s:%d in %s.close_pending_order",
                    res.comment, pending_order_ticket, self.symbol.name, self.ticket, self.__class__.__name__)
                return False, pending_order
        pending_order.order = res
        self.pending_orders.pop(pending_order_ticket, None)
        return True, pending_order

    async def update_position(self) -> bool:
        """Refresh position data from the broker.
        
        Queries the broker for current position data and updates the
        is_open status.
        
        Returns:
            True if the position is still open, False if closed.
        """
        try:
            pos = await self.positions.get_position_by_ticket(ticket=self.ticket)
            if pos is not None:
                self.position = pos
                self.is_open = True
            else:
                self.is_open = False
            return self.is_open
        except Exception as exe:
            logger.critical("%s: Error occurred while updating position for %s:%d in %s.update_position",
             exe, self.symbol.name, self.ticket, self.__class__.__name__)
            return self.is_open

    async def modify_stops(self, *, sl: float = None, tp: float = None,
                           use_stop_levels: bool = False) -> tuple[bool, OrderSendResult | None]:
        """Modify the stop loss and/or take profit levels.
        
        Args:
            sl: New stop loss price. Defaults to None (no change).
            tp: New take profit price. Defaults to None (no change).
            use_stop_levels: If True, validate and adjust stops against
                broker's minimum stop level requirements. Defaults to False.
                
        Returns:
            Tuple of (success, OrderSendResult). On failure, result may
            contain error details.
        """
        try:
            tick = await self.symbol.info_tick()

            if sl is not None and use_stop_levels is True:
                min_stops_value = (self.symbol.trade_stops_level + self.symbol.spread) * self.symbol.point
                if OrderType(self.position.type).is_long:
                    sl = min(sl, tick.ask - min_stops_value)
                elif OrderType(self.position.type).is_short:
                    sl = max(sl, tick.bid + min_stops_value)
                else:
                    logger.critical("Invalid OrderType cannot modify stops for %d:%s In %s.modify_stops",
                     self.ticket, self.symbol.name,self.__class__.__name__)
                    return False, None

            elif sl is not None and use_stop_levels is False:
                sl = sl or self.position.sl

            # modify take_profit
            if tp is not None and use_stop_levels is True:
                min_stops_value = (self.symbol.trade_stops_level + self.symbol.spread) * self.symbol.point
                if OrderType(self.position.type).is_long:
                    tp = max(tp, tick.ask + min_stops_value)
                elif OrderType(self.position.type).is_short():
                    tp = min(tp, tick.bid - min_stops_value)
                else:
                    logger.critical("Invalid OrderType cannot modify stops for %d:%s In %s.modify_stops",
                     self.ticket, self.symbol.name,self.__class__.__name__)
                    return False, None
            elif tp is not None and use_stop_levels is False:
                tp = tp or self.position.tp

            # send order
            order = Order(position=self.ticket, sl=sl, tp=tp, action=TradeAction.SLTP)
            res = await order.send()
            if res.retcode == 10009:
                await self.update_position()
                return True, res
            else:
                comment = res.comment if res else ""
                logger.critical("Unable to modify stops for %d:%s In %s.modify_stops: %s", self.ticket,
                 self.symbol.name,self.__class__.__name__, comment)
                return False, res
        except Exception as exe:
            logger.error("%s: Error occurred in %s.modify_stops for %s:%d",
                         exe, self.__class__.__name__, self.symbol.name, self.ticket)
            return False, None

    def remove_from_state(self):
        """Remove this position from state tracking and archive it.
        
        Moves the position from the active tracked positions to the
        archived positions in the state.
        """
        try:
            pos = self.config.state.get(self.state_key, {}).pop(self.ticket, None)
            self.config.state.setdefault(self.archive_key, {}).setdefault(self.ticket, pos) if pos else ...
        except KeyError as err:
            logger.error("%s: Unable to remove closed position from state in %s", err, self.__class__.__name__)

    async def close_position(self) -> tuple[bool, OrderSendResult | None]:
        """Close this position.
        
        Attempts to close the position and performs cleanup based on
        configuration (closing pending orders, hedges, stacks, etc.).
        
        Returns:
            Tuple of (success, OrderSendResult). On failure, result
            contains error details.
        """
        try:
            res = await self.positions.close_position(position=self.position)
            if not res[0]:
                logger.critical("Unable to close position for %d:%s In %s.close_position: %s", self.ticket,
                                self.symbol.name, self.__class__.__name__, res[1].comment)
                return res
            self.is_open = False
            closures = []
            if self.close_pending_orders_on_close:
                closures.append(self.close_pending_orders())
            if self.close_hedges_on_close:
                closures.append(self.close_hedges())
            if self.close_stacks_on_close:
                closures.append(self.close_stacks())
            await asyncio.gather(*closures, return_exceptions=True)
            if self.remove_from_state_on_close:
                self.remove_from_state()
            return res
        except Exception as exe:
            logger.error("%s: Error occurred in %s.close_position for %s:%d", exe, self.__class__.__name__,
                         self.symbol.name, self.ticket)
            return False, None

    async def close_hedges(self):
        """Close all hedge positions associated with this position.
        
        Attempts to close all positions in the hedges dictionary
        concurrently. Exceptions are logged but not re-raised.
        """
        try:
            hedges = tuple(self.hedges.values())
            await asyncio.gather(*[hedge.close_position() for hedge in hedges], return_exceptions=True)
        except Exception as exe:
            logger.error("%s: Error occurred in %s.close_hedges for %s:%d", exe, self.__class__.__name__,
                         self.symbol.name, self.ticket)

    async def close_stacks(self):
        """Close all stack positions associated with this position.
        
        Attempts to close all positions in the stacks dictionary
        concurrently. Exceptions are logged but not re-raised.
        """
        try:
            stacks = tuple(self.stacks.values())
            await asyncio.gather(*[stack.close_position() for stack in stacks], return_exceptions=True)
        except Exception as exe:
            logger.error("%s: Error occurred in %s.close_stacks for %s:%d", exe, self.__class__.__name__,
                         self.symbol.name, self.ticket)

    async def check_pending_order(self, *, pending_order: PendingOrder):
        """Check if a pending order has been filled and create position.
        
        If the pending order is now a position, creates a new OpenPosition
        and adds it to the appropriate collection (hedges or stacks).
        
        Args:
            pending_order: The PendingOrder to check.
        """
        try:
            pos = await self.positions.get_position_by_ticket(ticket=pending_order.order.order)
            if pos is None:
                return
            if pending_order.is_hedge:
                self.hedges[pos.ticket] = OpenPosition(symbol=self.symbol, position=pos, ticket=pos.ticket,
                                          is_a_hedge=True, hedge=self, **pending_order.open_pos_params)
                self.pending_orders.pop(pending_order.order.order)
            elif pending_order.is_stack:
                self.stacks[pos.ticket] = OpenPosition(symbol=self.symbol, position=pos, ticket=pos.ticket, 
                    is_a_stack=True, stack=self, **pending_order.open_pos_params)
                self.pending_orders.pop(pending_order.order.order)
            else:
                logger.warning("Unexpected pending order (neither hedge nor stack) for %s:%d", 
                   self.symbol.name, pending_order.order.order)
        except Exception as exe:
            logger.error("%s: Error occurred in %s.check_pending_hedge_order for %s:%d", exe, self.__class__.__name__,
                         self.symbol.name, self.ticket)
    
    @staticmethod
    async def check_pending_orders(self, /):
        """Check if any pending orders have been filled and create positions.
        
        Iterates through all pending orders and checks if they have been filled.
        If a pending order is now a position, creates a new OpenPosition
        and adds it to the appropriate collection (hedges or stacks).
        """
        try:
            orders = list(self.pending_orders.values())
            await asyncio.gather(*[self.check_pending_order(pending_order=pending_order) for pending_order in orders], return_exceptions=True)
        except Exception as exe:
            logger.error("%s: Error occurred in %s.check_pending_orders for %s:%d", exe, self.__class__.__name__,
                         self.symbol.name, self.ticket)

    async def track(self):
        """Execute all registered trackers on this position.
        
        Iterates through all trackers in rank order and executes them.
        Exceptions are logged but do not stop subsequent trackers.
        """
        try:
            for tracker in self.trackers:
                await tracker()
        except Exception as exe:
            logger.error("%s: Error occurred in %s.track for %s:%d", exe, self.__class__.__name__, self.symbol.name, self.ticket)

    async def profit_to_price(self, *, profit: float) -> float:
        """Calculate the price level that would yield a specific profit.
        
        Uses the broker's profit calculation to determine what price
        the position would need to reach to achieve the target profit.
        
        Args:
            profit: Target profit in account currency.
            
        Returns:
            The price level at which the position would have the target profit.
        """
        action = self.position.type
        volume = self.position.volume
        price_open = self.position.price_open
        price_close = increase_value_by_pct(price_open, 50) if self.position.type.is_long else decrease_value_by_pct(price_open, 50)
        half_profit = await Order.mt5.order_calc_profit(symbol=self.symbol.name, action=action, volume=volume,
                                             price_open=price_open, price_close=price_close)
        rate = profit / half_profit * 50
        rate = increase_value_by_pct(price_open, rate) if self.position.type.is_long else decrease_value_by_pct(price_open, rate)
        return rate

    async def hedge_order(self, *, price: float, order_params: dict = None,
                          open_pos_params: dict = None) -> tuple[bool, OrderSendResult | None]:
        """Place a pending hedge order at a specified price.
        
        Creates a pending order in the opposite direction that will become
        a hedge position when filled.
        
        Args:
            price: The price at which to place the pending order.
            order_params: Optional dictionary of order parameters to override
                defaults (type, volume, action, symbol, comment).
            open_pos_params: Optional parameters to apply to the OpenPosition
                created when the order is filled.
                
        Returns:
            Tuple of (success, OrderSendResult).
        """
        try:
            order_params = order_params or {}
            open_pos_params = open_pos_params or {}
            order_type = order_params.pop("type", OrderType.SELL_STOP if self.position.type.is_long else OrderType.BUY_STOP)
            volume = order_params.pop("volume", self.position.volume)
            action = order_params.pop("action", TradeAction.PENDING)
            symbol = order_params.pop("symbol", self.symbol.name)
            comment = order_params.pop("comment", f"Hedge_{self.symbol.name}:{self.ticket}")
            order = Order(action=action, symbol=symbol, type=order_type, price=price, volume=volume, comment=comment, **order_params)
            res = await order.send()
            if res.retcode != 10009:
                logger.critical("Unable to send pending order for %d:%s In %s.hedge_order: %s, %f", self.ticket,
                 self.symbol.name, self.__class__.__name__, res.comment, price)
                return False, res
            pending_order = PendingOrder(order=res, is_hedge=True, open_pos_params=open_pos_params)
            self.pending_orders[res.order] = pending_order
            self.is_hedged = True
            return True, res
        except Exception as exe:
            logger.error("%s: Error occurred in %s.hedge_order for %s:%d", exe, self.__class__.__name__, self.symbol.name, self.ticket)
            return False, None
        
    async def stack_order(self, *, price: float, order_params: dict = None,
                          open_pos_params: dict = None) -> tuple[bool, OrderSendResult | None]:
        """Place a pending stack order at a specified price.
        
        Creates a pending order in the same direction that will become
        a stack position when filled, adding to the current position.
        
        Args:
            price: The price at which to place the pending order.
            order_params: Optional dictionary of order parameters to override
                defaults (type, volume, action, symbol, comment).
            open_pos_params: Optional parameters to apply to the OpenPosition
                created when the order is filled.
                
        Returns:
            Tuple of (success, OrderSendResult).
        """
        try:
            order_params = order_params or {}
            open_pos_params = open_pos_params or {}
            order_type = order_params.pop("type", OrderType.BUY_STOP if self.position.type.is_long else OrderType.SELL_STOP)
            volume = order_params.pop("volume", self.position.volume)
            action = order_params.pop("action", TradeAction.PENDING)
            symbol = order_params.pop("symbol", self.symbol.name)
            comment = order_params.pop("comment", f"Stack_{self.symbol.name}:{self.ticket}")
            order = Order(action=action, symbol=symbol, type=order_type, price=price, volume=volume, comment=comment, **order_params)
            res = await order.send()
            if res.retcode != 10009:
                logger.critical("Unable to send pending order for %d:%s In %s.stack_order: %s", self.ticket,
                 self.symbol.name, self.__class__.__name__, res.comment)
                return False, res
            pending_order = PendingOrder(order=res, is_stack=True, open_pos_params=open_pos_params)
            self.pending_orders[res.order] = pending_order
            self.is_stacked = True
            return True, res
        except Exception as exe:
            logger.error("%s: Error occurred in %s.hedge_order for %s:%d", exe, self.__class__.__name__, self.symbol.name, self.ticket)
            return False, None
    
    def update(self, **kwargs):
        """Update position attributes.
        
        Args:
            **kwargs: Attribute name-value pairs to update.
        """
        [setattr(self, attr, value) for attr, value in kwargs.items()]

    async def hedge_position(self, *, order_params: dict = None, 
                             open_pos_params: dict = None) -> tuple[bool, OrderSendResult | None]:
        """Immediately open a hedge position.
        
        Opens a position in the opposite direction at current market price
        to hedge the current position.
        
        Args:
            order_params: Optional dictionary of order parameters to override
                defaults (volume, type, symbol, price, comment).
            open_pos_params: Optional parameters to apply to the created
                OpenPosition.
                
        Returns:
            Tuple of (success, OpenPosition) for the created hedge.
        """
        try:
            order_params = order_params or {}
            open_pos_params = open_pos_params or {}
            volume = order_params.pop("volume", self.position.volume)
            order_type = order_params.pop("type", OrderType(self.position.type).opposite)
            symbol = order_params.pop("symbol", self.symbol.name)
            if (price := order_params.pop("price", None)) is None:
                tick = await self.symbol.info_tick(name=symbol)
                price = (tick.ask if order_type.is_long else tick.bid)
            comment = order_params.pop("comment", f"Hedge:{self.symbol.name}:{self.ticket}")
            hedge_order = Order(type=order_type, symbol=symbol, volume=volume, price=price, comment=comment, **order_params)
            res = await hedge_order.send()
            if res.retcode != 10009:
                logger.critical("Unable to send hedge order for %d:%s In %s.hedge_position: %s", self.ticket,
                 self.symbol.name, self.__class__.__name__, res.comment)
                return False, res
            hedge_pos = await self.positions.get_position_by_ticket(ticket=res.order)
            if hedge_pos is None:
                logger.critical("Position not found for %d:%s In %s.hedge_position",
                                self.ticket, self.symbol.name, self.__class__.__name__)
                return False, res
            hedge = OpenPosition(symbol=symbol, ticket=res.order, position=hedge_pos, hedge=self, is_a_hedge=True, **open_pos_params)
            self.hedges[res.order] = hedge
            self.is_hedged = True
            return True, res
        except Exception as exe:
            logger.error("%s: Error occurred in %s.hedge_position for %s:%d", exe, self.__class__.__name__,
                         self.symbol.name, self.ticket)
            return False, None

    async def stack_position(self, *, order_params: dict = None,
                             open_pos_params: dict = None) -> tuple[bool, OrderSendResult | None]:
        """Immediately open a stack position.
        
        Opens a position in the same direction at current market price
        to add to the current position.
        
        Args:
            order_params: Optional dictionary of order parameters to override
                defaults (volume, type, symbol, price, comment).
            open_pos_params: Optional parameters to apply to the created
                OpenPosition.
                
        Returns:
            Tuple of (success, OpenPosition) for the created stack.
        """
        try:
            order_params = order_params or {}
            open_pos_params = open_pos_params or {}
            volume = order_params.pop("volume", self.position.volume)
            order_type = order_params.pop("type", self.position.type)
            symbol = order_params.pop("symbol", self.symbol.name)
            if (price := order_params.pop("price", None)) is None:
                tick = await self.symbol.info_tick(name=symbol)
                price = (tick.ask if order_type == OrderType.BUY else tick.bid)
            comment = order_params.pop("comment", f"Stack:{self.symbol.name}:{self.ticket}")
            stack_order = Order(type=order_type, symbol=symbol, volume=volume, price=price, comment=comment, **order_params)
            res = await stack_order.send()
            if res.retcode != 10009:
                logger.critical("Unable to send stack order for %d:%s In %s.stack_position: %s", self.ticket,
                 self.symbol.name, self.__class__.__name__, res.comment)
                return False, res
            stack_pos = await self.positions.get_position_by_ticket(ticket=res.order)
            if stack_pos is None:
                logger.critical("Position not found for %d:%s In %s.stack_position",
                                self.ticket, self.symbol.name, self.__class__.__name__)
                return False, res
            stack = OpenPosition(symbol=symbol, ticket=res.order, position=stack_pos, stack=self, is_a_stack=True, **open_pos_params)
            self.is_stacked = True
            self.stacks[res.order] = stack
            return True, res
        except Exception as exe:
            logger.error("%s: Error occurred in %s.stack_position for %s:%d", exe, self.__class__.__name__,
                         self.symbol.name, self.ticket)
            return False, None
