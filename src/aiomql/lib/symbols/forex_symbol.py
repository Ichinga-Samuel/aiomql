from ...symbol import Symbol
from ...core.exceptions import VolumeError

class ForexSymbol(Symbol):
    """Subclass of Symbol for Forex Symbols. Handles the conversion of currency and the computation of stop loss,
    take profit and volume.
    """
    def compute_points(self, *, amount: float, volume) -> float:
        """Compute the number of points required for a trade. Given the amount and the volume of the trade.
        Args:
            amount (float): Amount to trade
            volume (float): Volume to trade
        """
        points = amount / (volume * self.point * self.trade_contract_size)
        return points
    
    async def compute_volume_points(self, *, amount: float, points: float, use_limits=False, round_down: bool = True,
                                    adjust: float = False) -> tuple[float, float]:
        """Compute the volume and points required for a trade. Given the amount and the number of points.

        Args:
            amount (float): Amount to trade
            points (float): Number of points
            round_down: round down the computed volume to the nearest step default True
            adjust: Adjust the points if the computed volume is outside the range of permitted volumes
            use_limits: Adjust the computed volume to the nearest permitted volume if the computed volume is outside
        """
        amount = await self.check_amount(amount)
        volume = amount / (self.point * points * self.trade_contract_size)
        volume = self.round_off_volume(volume, round_down=round_down)
        if (chk_vol := self.check_volume(volume))[0]:
            if adjust:
                points = self.compute_points(amount=amount, volume=volume)
            return volume, points

        if use_limits:
            vol = chk_vol[1]
            if adjust:
                points = self.compute_points(amount=amount, volume=vol)
            return vol, points
        raise VolumeError(f"Incorrect Volume. Computed Volume outside the range of permitted volumes")

    async def compute_volume_sl(self, *, amount: float, price: float, sl: float,
                                use_limits=False, adjust: bool = False, round_down: bool = True) -> tuple[float, float]:
        amount = await self.check_amount(amount)
        volume = amount / ((price - sl) * self.trade_contract_size)
        volume = self.round_off_volume(volume, round_down=round_down)
        sign = volume / abs(volume) if volume else 1
        if (chk_vol := self.check_volume(abs(volume)))[0]:
            if adjust:
                sl = price - (amount / (volume * self.trade_contract_size))
                return abs(volume), sl
            return abs(volume), sl
        if use_limits:
            vol = chk_vol[1] * sign
            if adjust:
                sl = price - (amount / (vol * self.trade_contract_size))
            return abs(vol), sl
        raise VolumeError(f"Incorrect Volume. Computed Volume outside the range of permitted volumes")

    async def compute_volume(self, *, amount: float, points, use_limits=False, round_down=True) -> float:
        """Compute volume given an amount to risk and target points. Round the computed volume to the nearest step.

        Args:
            amount (float): Amount to risk. Given in terms of the account currency.
            points (float): Target points.
            use_limits (bool): If True, the computed volume checked against the maximum and minimum volume.
            round_down: round down the computed volume to the nearest step default True

        Returns:
            float: volume

        Raises:
            VolumeError: If the computed volume is less than the minimum volume or greater than the maximum volume.
        """
        amount = await self.check_amount(amount)
        volume = amount / (self.point * points * self.trade_contract_size)
        volume = self.round_off_volume(volume, round_down=round_down)
        if self.check_volume(volume)[0]:
            return volume
        if use_limits:
            return self.check_volume(volume)[1]
        raise VolumeError(f"Incorrect Volume. Computed Volume outside the range of permitted volumes")