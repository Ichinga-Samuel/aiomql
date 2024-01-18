"""Risk Assessment and Management"""
from .account import Account


class RAM:
    account: Account
    risk_to_reward: float
    risk: float
    amount: float
    points: float
    pips: float
    min_amount: float
    max_amount: float

    def __init__(self, *, risk_to_reward: float = 1, risk: float = 0.01, amount: float = 0, **kwargs):
        """Initialize Risk Assessment and Management with the provided keyword arguments.

        Keyword Args:
            risk_to_reward (float): Risk to reward ratio. Defaults to 1
            risk (float): Percentage of account balance to risk per trade 0.01 # 1%
            amount (float): Amount to risk per trade in terms of account currency 0
            kwargs: extra keyword arguments are set as object attributes
        """
        self.risk_to_reward = risk_to_reward
        self.risk = risk
        self.amount = amount
        self.account = Account()
        [setattr(self, key, value) for key, value in kwargs.items()]

    async def get_amount(self) -> float:
        """Calculate the amount to risk per trade as a percentage of equity.

        Returns:
            float: Amount to risk per trade
        """
        await self.account.refresh()
        return self.account.equity * self.risk