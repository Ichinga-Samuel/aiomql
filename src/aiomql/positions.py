"""Handle Open positions."""
import asyncio
from logging import getLogger

from .core import MetaTrader, TradePosition, TradeAction, OrderType
from .order import Order

logger = getLogger(__name__)

class Positions:
    """Get Open Positions.

    Attributes:
        symbol (str): Financial instrument name.
        group (str): The filter for arranging a group of necessary symbols. Optional named parameter.
            If the group is specified, the function returns only positions meeting a specified criteria for a symbol name.
        ticket (int): Position ticket.
        mt5 (MetaTrader): MetaTrader instance.
    """
    mt5: MetaTrader = MetaTrader()
    
    def __init__(self, *, symbol: str = "", group: str = "", ticket: int = 0):
        """Get Open Positions.

        Keyword Args:
            symbol (str): Financial instrument name.
            group (str): The filter for arranging a group of necessary symbols. Optional named parameter. If the group
                is specified, the function returns only positions meeting a specified criteria for a symbol name.
            ticket (int): Position ticket

        """
        self.symbol = symbol
        self.group = group
        self.ticket = ticket

    async def positions_total(self) -> int:
        """Get the number of open positions.
        
        Returns:
            int: Return total number of open positions
        """
        return await self.mt5.positions_total()

    async def positions_get(self, symbol: str = '', group: str = '', ticket: int = 0):
        """Get open positions with the ability to filter by symbol or ticket.

        Keyword Args:
            symbol (str): Financial instrument name.
            group (str): The filter for arranging a group of necessary symbols. Optional named parameter. If the group
                is specified, the function returns only positions meeting a specified criteria for a symbol name.
            ticket (int): Position ticket
        
        Returns:
            list[TradePosition]: A list of open trade positions
        """
        symbol = symbol or self.symbol
        group = group or self.group
        ticket = ticket or self.ticket
        positions = await self.mt5.positions_get(group=group, symbol=symbol, ticket=ticket)
        if not positions:
            return []
        return [TradePosition(**pos._asdict()) for pos in positions]

    async def close_all(self, symbol: str = '', group: str = '') -> int:
        """Close all open positions for the trading account.

        Returns:
            int: Return number of positions closed.
        """
        orders = [Order(action=TradeAction.DEAL, price=pos.price_current, position=pos.ticket,
                        type=OrderType(pos.type).opposite,
                        **pos.get_dict(include={'symbol', 'volume'})) for pos in
                  (await self.positions_get(symbol=symbol, group=group))]

        results = await asyncio.gather(*[order.send() for order in orders], return_exceptions=True)
        amount_closed = len([res for res in results if res.retcode == 10009])
        pos = await self.positions_total()
        if pos > 0:
            logger.warning(f'Failed to close {pos} positions')
        else:
            logger.info('All positions closed')
        return amount_closed
