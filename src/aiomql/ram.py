"""Risk Assessment and Management"""
from .account import Account
from .symbol import Symbol


class RAM:
    account: Account = Account()
    risk_to_reward: float
    risk: float
    amount: float
    pips: float
    volume: float

    def __init__(self, **kwargs):
        """Risk Assessment and Management. All provided keyword arguments are set as attributes.

        Args:
            kwargs (Dict): Keyword arguments.

        Defaults:
            risk_to_reward (float): Risk to reward ratio 1
            risk (float): Percentage of account balance to risk per trade 0.01 # 1%
            amount (float): Amount to risk per trade in terms of account currency 0
            pips (float): Target pips 0
            volume (float): Volume to trade 0
        """
        self.risk_to_reward = kwargs.pop('risk_to_reward', 1)
        self.risk = kwargs.pop('risk', 0.01)
        self.amount = kwargs.pop('amount', 0)
        self.pips = kwargs.pop('pips', 0)
        self.volume = kwargs.pop('volume', 0)
        [setattr(self, key, value) for key, value in kwargs.items()]

    async def get_amount(self, risk: float = 0) -> float:
        """Calculate the amount to risk per trade as a percentage of free margin.

        Keyword Args:
            risk (float): Percentage of account balance to risk per trade. Defaults to zero.

        Returns:
            float: Amount to risk per trade
        """
        await self.account.refresh()
        risk = risk or self.risk
        return self.account.margin_free * risk

    async def get_volume(self, *, symbol: Symbol, pips: float = 0, amount: float = 0) -> float:
        """Calculate the volume to trade. if pips is not provided, the pips attribute is used.
        If the amount attribute or amount argument is zero, the amount is calculated using the get_amount method based on the risk.

        Args:
            symbol (Symbol): Financial instrument

        Keyword Args:
            pips (float): Target pips. Defaults to zero.
            amount (float): Amount to risk per trade. Defaults to zero.

        Returns:
            float: Volume to trade
        """
        pips = pips or self.pips
        amount = amount or self.amount or await self.get_amount()
        return await symbol.compute_volume(amount=amount, pips=pips)

