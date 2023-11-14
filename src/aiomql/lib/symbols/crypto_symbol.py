from ...symbol import Symbol
from ...core.exceptions import VolumeError


class CryptoSymbol(Symbol):
    """Subclass of Symbol for Crypto/Fiat Symbols. Handles the computation of volume based on the amount to risk."""

    async def compute_volume(self, *, amount: float, points, use_limits=False) -> float:
        """Compute volume given an amount to risk and target pips. Round the computed volume to the nearest step.

        Args:
            amount (float): Amount to risk. Given in terms of the account currency.
            points (float): Target pips.
            use_limits (bool): If True, the computed volume checked against the maximum and minimum volume.

        Returns:
            float: volume

        Raises:
            VolumeError: If the computed volume is less than the minimum volume or greater than the maximum volume.
        """
        if self.currency_profit != self.account.currency:
            amount = await self.convert_currency(amount=amount, base=self.currency_profit, quote=self.account.currency)
        volume = amount / (self.point * points * self.trade_contract_size)
        volume = self.round_off_volume(volume)
        if self.check_volume(volume)[0]:
            return volume
        if use_limits:
            return self.check_volume(volume)[1]
        raise VolumeError(f'Incorrect Volume. Computed Volume outside the range of permitted volumes')
