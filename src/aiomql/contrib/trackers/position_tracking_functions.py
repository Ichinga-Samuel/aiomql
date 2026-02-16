"""Position tracking functions for managing open positions.

This module provides pre-built tracking functions that can be used with 
the PositionTracker class to implement common trading strategies like
trailing stops, take-profit extension, and checkpoint-based exits.

Functions:
    exit_at_price: Exit a trade when profit reaches a specified target or stop.
    extend_take_profit: Dynamically extend take profit as price moves favorably.
    exit_at_checkpoint: Trail-based exit strategy using checkpoints.
"""
from logging import getLogger

from .open_position import OpenPosition
from ...utils.price_utils import get_price_in_range_pct, extend_range_by_pct

logger = getLogger(__name__)


async def exit_at_profit(pos: OpenPosition, /, tp: float = None, sl: float = None):
    """Exit a trade when profit reaches a specified target or stop loss.
    
    Closes the position if the current profit meets or exceeds the take profit
    target, or falls to or below the stop loss threshold.
    
    Args:
        pos: The open position to monitor and potentially close.
        tp: Take profit target in account currency. Position closes if 
            profit >= tp. Defaults to None (no take profit check).
        sl: Stop loss threshold in account currency. Position closes if
            profit <= sl. Defaults to None (no stop loss check).
            
    Note:
        At least one of tp or sl should be provided for this function
        to have any effect.
    """
    if not await pos.update_position():
        return

    if (tp is not None and pos.position.profit >= tp) or (sl is not None and pos.position.profit <= sl):
        ok, res = await pos.close_position()
        if not ok:
            comment = res.comment if res is not None else ""
            logger.warning("Unable to close %s:%d due to %s in exit_at_price", pos.symbol.name, pos.ticket, comment)
        else:
            logger.info("Closed %s:%d in exit_at_price with profit %s", pos.symbol.name, pos.ticket, pos.position.profit)


async def extend_take_profit(pos: OpenPosition, /, increase: float = 20, start: float = 80,
                             use_stop_levels: bool = True):
    """Dynamically extend take profit as price moves favorably.
    
    When the current price reaches a specified percentage of the distance
    to take profit, extends the take profit by the given percentage.
    
    Args:
        pos: The open position to manage.
        increase: Percentage to extend the take profit distance by.
            Defaults to 20.
        start: Percentage of the distance to TP at which to trigger
            extension. Defaults to 80 (extend when 80% to TP).
        use_stop_levels: Whether to validate against broker's minimum
            stop levels. Defaults to True.
            
    Note:
        Only applies when position is in profit. Does nothing if position
        is closed or in loss.
    """
    is_open = await pos.update_position()
    if is_open is False or pos.position.profit < 0:
        return
    position = pos.position
    if get_price_in_range_pct(position.price_open, position.tp, position.price_current) >= start:
        new_tp = extend_range_by_pct(position.price_open, position.tp, increase)
        ok, res = await pos.modify_stops(tp=new_tp, use_stop_levels=use_stop_levels)
        if ok:
            logger.info("%s:%d take_profit extended by extend_take_profit", position.symbol, position.ticket)
        else:
            logger.warning("Unable to extend take profit of %s:%d due to %s in extend_take_profit",
                           position.symbol, position.ticket, res.comment)

