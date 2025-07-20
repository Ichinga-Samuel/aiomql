from logging import getLogger

from aiomql import OrderType

from .open_position import OpenPosition
from ..quants import extend_interval_by_percentage, get_percentage_position, percentage_position

logger = getLogger(__name__)


async def exit_at_price(*, pos: OpenPosition, tp: float = None, sl: float = None):
    """Exit a trade at a particular price"""
    if not await pos.update_position():
        return

    if (tp is not None and pos.position.profit >= tp) or (sl is not None and pos.position.profit <= sl):
        ok, res = await pos.close_position()
        if not ok:
            logger.warning("Unable to close %s:%d due to %s in exit_at_price", pos.symbol, pos.ticket, res.comment)


async def extend_take_profit(*, pos: OpenPosition, increase: float = 20, start: float = 80,
                             use_stop_levels: bool = True):
    is_open = await pos.update_position()
    if is_open is False or pos.position.profit < 0:
        return
    position = pos.position
    if percentage_position(position.price_open, position.tp, position.price_current) >= start:
        new_tp = extend_interval_by_percentage(position.price_open, position.tp, increase)
        ok, res = await pos.modify_stops(tp=new_tp, use_stop_levels=use_stop_levels)
        if ok:
            logger.info("%s:%d take_profit extended by extend_take_profit", position.symbol, position.ticket)
        else:
            logger.warning("Unable to extend take profit of %s:%d due to %s in extend_take_profit",
                           position.symbol, position.ticket, res.comment)


async def extend_stop_loss(*, pos: OpenPosition, increase: float = 20, start: float = 80,
                           use_stop_levels: bool = True):
    is_open = await pos.update_position()
    if is_open is False or pos.position.profit > 0:
        return
    position = pos.position
    if percentage_position(position.price_open, position.tp, position.price_current) >= start:
        new_sl = extend_interval_by_percentage(position.price_open, position.sl, increase)
        ok, res = await pos.modify_stops(sl=new_sl, use_stop_levels=use_stop_levels)
        if ok:
            logger.info("%s:%d extend_stop_loss extended by extend_stop_loss",
                        position.symbol, position.ticket)
        else:
            logger.warning("Unable to extend stop loss of %s:%d due to %s in extend_stop_loss",
                           position.symbol, position.ticket, res.comment)


async def exit_at_checkpoint(*, pos: OpenPosition, start: float = 80, trail: float = 15):
    is_open = await pos.update_position()
    if is_open is False or pos.position.profit < 0:
        return
    position = pos.position
    if percentage_position(position.price_open, position.tp, position.price_current) >= start:
        new_checkpoint = get_percentage_position(position.price_open, position.price_current, 100-trail)
        change_checkpoint = False
        if position.type == OrderType.BUY and new_checkpoint > pos.checkpoint:
            change_checkpoint = True
        elif position.type == OrderType.SELL and new_checkpoint < pos.checkpoint:
            change_checkpoint = True
        if change_checkpoint:
            pos.checkpoint = new_checkpoint
            pos.use_checkpoint = True
            logger.info("New checkpoint created for %s:%d at %f:%f",
                        position.symbol, position.ticket, new_checkpoint, position.profit)
    close = False
    if position.type == OrderType.BUY and position.price_current <= pos.checkpoint and pos.use_checkpoint:
        close = True

    elif position.type == OrderType.SELL and position.price_current >= pos.checkpoint and pos.use_checkpoint:
        close = True

    if close:
        ok, res = await pos.close_position()
        if not ok:
            logger.warning("Unable to close %s:%d due to %s in checkpoint", position.symbol,
                           position.ticket, res.comment)
        else:
            logger.info("Closed %s:%d in checkpoint at %f:%f",
                        position.symbol, position.ticket, position.price_current, position.profit)
