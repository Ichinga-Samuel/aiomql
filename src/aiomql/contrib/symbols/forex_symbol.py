"""Forex symbol module for handling forex trading instruments.

This module provides the ForexSymbol class, a specialized subclass of Symbol
designed for forex trading. It includes forex-specific calculations for pips,
points, and volume computations based on price movements and stop-loss levels.

Example:
    Basic usage of ForexSymbol::

        from aiomql.contrib.symbols import ForexSymbol

        # Create a forex symbol instance
        eurusd = ForexSymbol(name="EURUSD")
        await eurusd.initialize()

        # Get the pip value
        pip_value = eurusd.pip

        # Compute volume based on risk amount and stop loss
        volume = eurusd.compute_volume_sl(
            amount=100.0,
            price=1.1000,
            sl=1.0950
        )
"""

from ...lib.symbol import Symbol


class ForexSymbol(Symbol):
    """Subclass of Symbol for forex trading instruments.

    This class extends the base Symbol class with forex-specific functionality,
    including pip value calculations and volume computations based on points
    or stop-loss levels. It handles the conversion of currency and the
    computation of stop loss, take profit, and volume for forex trades.

    Attributes:
        tick (Tick): Price tick object for the instrument, inherited from Symbol.
        account (Account): Account object associated with the symbol, inherited from Symbol.

    Note:
        All monetary amounts should be in the account's base currency unless
        otherwise specified.
    """

    @property
    def pip(self) -> float:
        """Get the pip value of the forex symbol.

        For forex symbols, a pip is defined as ten times the point value.
        This is the standard convention where most forex pairs have a pip
        as the fourth decimal place (or second for JPY pairs).

        Returns:
            float: The pip value of the symbol, calculated as point * 10.

        Example:
            >>> eurusd = ForexSymbol(name="EURUSD")
            >>> await eurusd.initialize()
            >>> pip_value = eurusd.pip  # Returns 0.0001 for EURUSD
        """
        return self.point * 10

    def compute_points(self, *, amount: float, volume: float) -> float:
        """Compute the number of points required for a trade.

        Calculates how many points of price movement are needed to achieve
        a specified profit or loss amount given a particular trade volume.

        Args:
            amount (float): The monetary amount (profit/loss) to achieve,
                in the account's base currency.
            volume (float): The trade volume in lots.

        Returns:
            float: The number of points of price movement required.

        Example:
            >>> eurusd = ForexSymbol(name="EURUSD")
            >>> await eurusd.initialize()
            >>> # How many points for $50 profit with 0.1 lots
            >>> points = eurusd.compute_points(amount=50.0, volume=0.1)
        """
        points = amount / (volume * self.point * self.trade_contract_size)
        return points

    async def compute_volume_points(self, *, amount: float, points: float, round_down: bool = False) -> float:
        """Compute the volume required for a trade based on points.

        Calculates the appropriate trade volume to risk a specified amount
        over a given number of points of price movement.

        Args:
            amount (float): The monetary amount to risk, in the account's
                base currency.
            points (float): The number of points of price movement
                (e.g., stop loss distance in points).
            round_down (bool): If True, round down the computed volume to
                the nearest volume step. If False, round to the nearest
                step. Defaults to False.

        Returns:
            float: The computed volume, rounded to the symbol's volume step.

        Example:
            >>> eurusd = ForexSymbol(name="EURUSD")
            >>> await eurusd.initialize()
            >>> # Volume to risk $100 over 500 points
            >>> volume = eurusd.compute_volume_points(
            ...     amount=100.0,
            ...     points=500,
            ...     round_down=True
            ... )
        """
        volume = amount / (self.point * points * self.trade_contract_size)
        return self.round_off_volume(volume=volume, round_down=round_down)

    async def compute_volume_sl(self, *, amount: float, price: float, sl: float, round_down: bool = False) -> float:
        """Compute the volume required for a trade based on stop loss.

        Calculates the appropriate trade volume to risk a specified amount
        given the entry price and stop loss level. This is useful for
        position sizing based on a fixed monetary risk.

        Args:
            amount (float): The monetary amount to risk if stop loss is hit,
                in the account's base currency.
            price (float): The entry price of the trade.
            sl (float): The stop loss price level.
            round_down (bool): If True, round down the computed volume to
                the nearest volume step. If False, round to the nearest
                step. Defaults to False.

        Returns:
            float: The computed volume, rounded to the symbol's volume step.

        Example:
            >>> eurusd = ForexSymbol(name="EURUSD")
            >>> await eurusd.initialize()
            >>> # Volume to risk $100 with entry at 1.1000 and SL at 1.0950
            >>> volume = eurusd.compute_volume_sl(
            ...     amount=100.0,
            ...     price=1.1000,
            ...     sl=1.0950,
            ...     round_down=True
            ... )
        """
        volume = amount / (abs(price - sl) * self.trade_contract_size)
        return self.round_off_volume(volume=volume, round_down=round_down)
