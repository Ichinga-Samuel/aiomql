from collections.abc import Callable
from typing import Any, TypeVar
from logging import getLogger

logger = getLogger(__name__)

OpenPosition = TypeVar('OpenPosition')


class PositionTracker:
    params: dict[str, Any]
    function: Callable
    number: int
    open_position: OpenPosition

    def __init__(self, function: Callable, /, **kwargs) -> None:
        self.function = function
        self.kwargs = kwargs
        self.number = 0

    async def __call__(self, **kwargs):
        try:
            kwargs = self.kwargs if not kwargs else (self.kwargs | kwargs)
            await self.function(self.open_position, **kwargs)
        except Exception as exe:
            logger.error("%s: Error occurred in %s for %s:%d", exe, self.function.__name__,
                         self.open_position.symbol.name, self.open_position.ticket)

    def set_position(self, open_position: "OpenPosition", number: int = None):
        self.open_position = open_position
        if number is not None:
            self.number = number
        self.open_position = open_position
