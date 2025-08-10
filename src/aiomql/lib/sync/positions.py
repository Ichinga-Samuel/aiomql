"""Handle Open positions."""
from logging import getLogger

from ...core.meta_trader import MetaTrader
from ...core.models import TradePosition, OrderSendResult
from ...core.constants import OrderType, TradeAction
from ...core.config import Config
from ...core.sync.meta_trader import MetaTrader
from ..order import Order


logger = getLogger(__name__)


class Positions:
    """Get Open Positions.

    Attributes:
        mt5 (MetaTrader): MetaTrader instance.
    """
    mt5: MetaTrader
    config: Config
    positions: tuple[TradePosition, ...]

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "config"):
            cls.config = Config()
        if not hasattr(cls, "mt5"):
            cls.mt5 = MetaTrader()
        return super().__new__(cls)

    def __init__(self):
        self.positions = ()

    def get_positions(self, *, symbol: str = None, ticket: int = None, group: str = None) -> tuple[TradePosition, ...]:
        """Get open positions with the ability to filter by symbol, ticket or group of symbols.
        Args:
            symbol (Optional[str]): Financial instrument name. If a symbol is provided, the ticket is ignored.
            ticket (Optional[int]): Position ticket.
            group (Optional[str]): Group of symbols.

        Returns:
            tuple[TradePosition, ...]: A tuple of open trade positions
        """
        kwargs = {}
        if symbol is not None:
            kwargs["symbol"] = symbol
            ticket = None
        if ticket is not None:
            kwargs["ticket"] = ticket
        if group is not None:
            kwargs["group"] = group
        positions = self.mt5.positions_get(**kwargs)
        if positions is not None:
            return tuple(TradePosition(**pos._asdict()) for pos in positions)
        logger.warning("Failed to get open positions")
        return ()

    def get_position_by_ticket(self, *, ticket: int) -> TradePosition | None:
        """Get an open position by ticket.
        Args:
            ticket (int): Position ticket.

        Returns:
            TradePosition: Return an open position
        """
        positions = self.mt5.positions_get(ticket=ticket)
        position = positions[0] if positions else None
        if position is None or position.ticket != ticket:
            return None
        return TradePosition(**position._asdict())

    def get_positions_by_symbol(self, *, symbol: str) -> tuple[TradePosition, ...]:
        """Get open positions by symbol.
        Args:
            symbol (str): Financial instrument name.

        Returns:
            tuple[TradePosition, ...]: A tuple of open trade positions
        """
        positions = self.mt5.positions_get(symbol=symbol)
        return tuple(TradePosition(**pos._asdict()) for pos in (positions or ()))

    @staticmethod
    def close(*, ticket: int, symbol: str, price: float, volume: float, order_type: OrderType) -> OrderSendResult:
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
        return order.send()

    def close_position_by_ticket(self, *, ticket: int) -> OrderSendResult | None:
        """Close an open position using the ticket."""
        position = self.get_position_by_ticket(ticket=ticket)
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
        return order.send()

    @staticmethod
    def close_position(*, position: TradePosition):
        """Close an open position for the trading account. Using a position object."""
        order = Order(
            position=position.ticket,
            symbol=position.symbol,
            volume=position.volume,
            type=position.type.opposite,
            price=position.price_current,
            action=TradeAction.DEAL,
        )
        return order.send()

    def close_all(self) -> int:
        """Close all open positions for the trading account. Specify a symbol or group to filter positions.

        Returns:
            int: Return number of positions closed.
        """
        positions = self.get_positions()
        results = [self.close_position(position=position) for position in positions]

        return len([res for res in results if (isinstance(res, OrderSendResult) and res.retcode == 10009)])

    def get_total_positions(self) -> int:
        """Get the total number of open positions."""
        return self.mt5.positions_total()
