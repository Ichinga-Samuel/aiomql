from ...lib.symbol import Symbol


class ForexSymbol(Symbol):
    """Subclass of Symbol for Forex Symbols. Handles the conversion of currency and the computation of stop loss,
    take profit and volume.
    """

    @property
    def pip(self):
        """Returns the pip value of the symbol. This is ten times the point value for forex symbols.

        Returns:
            float: The pip value of the symbol.
        """
        return self.point * 10

    def compute_points(self, *, amount: float, volume: float) -> float:
        """Compute the number of points required for a trade. Given the amount and the volume of the trade.
        Args:
            amount (float): Amount to trade
            volume (float): Volume to trade
        """
        points = amount / (volume * self.point * self.trade_contract_size)
        return points
    
    async def compute_volume_points(self, *, amount: float, points: float, round_down: bool = False) -> float:
        """Compute the volume required for a trade. Given the amount and the number of points.

        Args:
            amount (float): Amount to trade
            points (float): Number of points
            round_down: round down the computed volume to the nearest step default True
        """
        volume = amount / (self.point * points * self.trade_contract_size)
        return self.round_off_volume(volume=volume, round_down=round_down)

    async def compute_volume_sl(self, *, amount: float, price: float, sl: float, round_down: bool = False) -> float:
        volume = amount / (abs(price - sl) * self.trade_contract_size)
        return self.round_off_volume(volume=volume, round_down=round_down)
