"""Handle Open positions."""

import asyncio
from logging import getLogger

from ..core.meta_trader import MetaTrader
from ..core.models import TradePosition, OrderSendResult
from ..core.constants import OrderType, TradeAction
from ..core.config import Config
from .._utils import backoff_decorator
from ..core.meta_backtester import MetaBackTester
from .order import Order


logger = getLogger(__name__)


class Positions:
    """Get Open Positions.

    Attributes:
        mt5 (MetaTrader): MetaTrader instance.
    """

    mt5: MetaTrader | MetaBackTester
    positions: tuple[TradePosition, ...]

    def __init__(self):
        """Get Open Positions"""
        self.config = Config()
        self.mt5 = MetaTrader() if self.config.mode != "backtest" else MetaBackTester()
        self.positions = ()

    @backoff_decorator
    async def get_positions(self) -> tuple[TradePosition, ...]:
        """Get open positions with the ability to filter by symbol or ticket.

        Returns:
            tuple[TradePosition, ...]: A tuple of open trade positions
        """
        positions = await self.mt5.positions_get()
        if positions is not None:
            self.positions = tuple(TradePosition(**pos._asdict()) for pos in positions)
            return self.positions
        logger.warning("Failed to get open positions")
        return ()

    async def get_position_by_ticket(self, *, ticket: int) -> TradePosition | None:
        """Get an open position by ticket.
        Args:
            ticket (int): Position ticket.

        Returns:
            TradePosition: Return an open position
        """
        positions = await self.mt5.positions_get(ticket=ticket)
        position = positions[0] if positions else None
        if position is None or position.ticket != ticket:
            return None
        return TradePosition(**position._asdict())

    async def get_positions_by_symbol(self, *, symbol: str) -> tuple[TradePosition, ...]:
        """Get open positions by symbol.
        Args:
            symbol (str): Financial instrument name.

        Returns:
            tuple[TradePosition, ...]: A tuple of open trade positions
        """
        positions = await self.mt5.positions_get(symbol=symbol)
        return tuple(TradePosition(**pos._asdict()) for pos in (positions or ()))

    @staticmethod
    async def close(*, ticket: int, symbol: str, price: float, volume: float, order_type: OrderType) -> OrderSendResult:
        """Close an open position for the trading account using the ticket and other parameters.

        Args:
            ticket (int): Position ticket.
            symbol (str): Financial instrument name.
            price (float): Closing price.
            volume (float): Volume to close.
            order_type (OrderType): Order type.
        """
        order = Order(
            action=TradeAction.DEAL,
            price=price,
            position=ticket,
            symbol=symbol,
            volume=volume,
            type=order_type.opposite,
        )
        return await order.send()

    async def close_position_by_ticket(self, *, ticket: int) -> OrderSendResult | None:
        """Close an open position using the ticket."""
        position = await self.get_position_by_ticket(ticket=ticket)
        if position is None:
            return None
        order = Order(
            position=position.ticket,
            symbol=position.symbol,
            volume=position.volume,
            type=position.type.opposite,
            price=position.price_current,
            action=TradeAction.DEAL,
        )
        return await order.send()

    @staticmethod
    async def close_position(*, position: TradePosition):
        """Close an open position for the trading account. Using a position object."""
        order = Order(
            position=position.ticket,
            symbol=position.symbol,
            volume=position.volume,
            type=position.type.opposite,
            price=position.price_current,
            action=TradeAction.DEAL,
        )
        return await order.send()

    async def close_all(self) -> int:
        """Close all open positions for the trading account. Specify a symbol or group to filter positions.

        Returns:
            int: Return number of positions closed.
        """
        positions = self.positions or await self.get_positions()
        results = await asyncio.gather(
            *(self.close_position(position=position) for position in positions), return_exceptions=True
        )
        return len([res for res in results if (isinstance(res, OrderSendResult) and res.retcode == 10009)])
