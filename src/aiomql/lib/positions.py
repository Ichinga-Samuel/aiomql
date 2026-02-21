"""Positions module for managing open trading positions.

This module provides the Positions class for retrieving, managing, and
closing open positions in the MetaTrader 5 terminal.

Example:
    Getting and closing positions::

        positions = Positions()
        open_positions = await positions.get_positions(symbol='EURUSD')
        closed_count = await positions.close_all()
"""

import asyncio
from logging import getLogger

from ..core.meta_trader import MetaTrader
from ..core.base import BaseMeta
from ..core.models import TradePosition, OrderSendResult
from ..core.constants import OrderType, TradeAction
from ..core.config import Config
from ..core.exceptions import InvalidRequest
from .order import Order


logger = getLogger(__name__)

class Positions(metaclass=BaseMeta):
    """Get Open Positions.

    Attributes:
        mt5 (MetaTrader): MetaTrader instance.
    """
    mt5: MetaTrader
    config: Config

    @classmethod
    async def get_positions(cls, *, symbol: str = None, ticket: int = None, group: str = None) -> tuple[TradePosition, ...]:
        kwargs = {}
        if symbol is not None:
            kwargs["symbol"] = symbol
            ticket = None
        if ticket is not None:
            kwargs["ticket"] = ticket
        if group is not None:
            kwargs["group"] = group
        positions = await cls.mt5.positions_get(**kwargs)
        if positions is not None:
            return tuple(TradePosition(**pos._asdict()) for pos in positions)
        logger.warning("Failed to get open positions")
        return ()

    @classmethod
    async def get_position_by_ticket(cls, *, ticket: int) -> TradePosition | None:
        """Get an open position by ticket.
        Args:
            ticket (int): Position ticket.

        Returns:
            TradePosition: Return an open position
        """
        positions = await cls.get_positions(ticket=ticket)
        return pos if len(positions) and (pos := positions[0]).ticket == ticket else None

    @classmethod
    async def get_positions_by_symbol(cls, *, symbol: str) -> tuple[TradePosition, ...]:
        """Get open positions by symbol.
        Args:
            symbol (str): Financial instrument name.

        Returns:
            tuple[TradePosition, ...]: A tuple of open trade positions
        """
        return await cls.get_positions(symbol=symbol)

    @staticmethod
    async def close(*, ticket: int, symbol: str, price: float, volume: float, order_type: OrderType) -> tuple[bool, OrderSendResult]:
        """Close an open position for the trading account using the ticket and other parameters.

        Args:
            ticket (int): Position ticket.
            symbol (str): Financial instrument name.
            price (float): Closing price.
            volume (float): Volume to close.
            order_type (OrderType): Order type.
        """
        req = dict(action=TradeAction.DEAL, price=price, position=ticket, symbol=symbol, volume=volume,
                   type=OrderType(order_type).opposite)
        res = await Order.send_order(request=req)
        if res.retcode != 10009:
            cop = await Order.get_history_order_by_ticket(ticket=ticket)
            res.comment = f"{res.comment}: Position is already closed"
            if cop is None:
                return False, res
        return True, res

    @classmethod
    async def close_position_by_ticket(cls, *, ticket: int) -> tuple[bool, OrderSendResult]:
        """Close an open position using the ticket."""
        position = await cls.get_position_by_ticket(ticket=ticket)
        if position is None:
            cop = await Order.get_history_order_by_ticket(ticket=ticket)
            if cop is None:
                raise InvalidRequest("Failed to get open position with %d" % ticket)
            return True, OrderSendResult(order=ticket, comment="Position is already closed")
        return await cls.close_position(position=position)

    @staticmethod
    async def close_position(*, position: TradePosition) -> tuple[bool, OrderSendResult]:
        """Close an open position for the trading account. Using a position object."""
        req = dict(position=position.ticket, symbol=position.symbol, volume=position.volume,
                   type=position.type.opposite, price=position.price_current, action=TradeAction.DEAL)
        res = await Order.send_order(request=req)
        if res.retcode != 10009:
            cop = await Order.get_history_order_by_ticket(ticket=position.ticket)
            res.comment = f"{res.comment}: Position is already closed"
            if cop is None:
                return False, res
        return True, res
    
    @classmethod
    async def close_positions(cls, *, positions: tuple[TradePosition, ...]) -> tuple[tuple[bool, OrderSendResult], ...]:
        """Close open positions for the trading account."""
        results = await asyncio.gather(
            *(cls.close_position(position=position) for position in positions), return_exceptions=True
        )
        return tuple(res for res in results if isinstance(res, tuple) and res[0])

    @classmethod
    async def close_all_positions(cls) -> tuple[OrderSendResult, ...]:
        positions = await cls.get_positions()
        if positions is None:
            return ()
        results = await asyncio.gather(
            *(cls.close_position(position=position) for position in positions), return_exceptions=True
        )
        return tuple(res[1] for res in results if isinstance(res, tuple) and res[0])

    @classmethod
    async def get_total_positions(cls) -> int:
        """Get the total number of open positions."""
        return await cls.mt5.positions_total()
