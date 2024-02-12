"""Risk Assessment and Management"""
from .account import Account
from .positions import Positions


class RAM:
    account: Account
    risk_to_reward: float
    risk: float
    points: float
    pips: float
    min_amount: float
    max_amount: float
    balance_level: float = 10
    loss_limit: int = 3

    def __init__(self, *, risk_to_reward: float = 1, risk: float = 0.01, **kwargs):
        """Initialize Risk Assessment and Management with the provided keyword arguments.

        Keyword Args:
            risk_to_reward (float): Risk to reward ratio. Defaults to 1
            risk (float): Percentage of account balance to risk per trade 0.01 # 1%
            kwargs: extra keyword arguments are set as object attributes
        """
        self.risk_to_reward = risk_to_reward
        self.risk = risk
        self.account = Account()
        [setattr(self, key, value) for key, value in kwargs.items()]

    async def get_amount(self) -> float:
        """Calculate the amount to risk per trade as a percentage of balance.

        Returns:
            float: Amount to risk per trade
        """
        await self.account.refresh()
        return self.account.balance * self.risk

    async def check_losing_positions(self) -> bool:
        """Check if the number of losing positions is greater than or equal the loss limit."""
        positions = await Positions().positions_get()
        positions.sort(key=lambda pos: pos.time_msc)
        loosing = [trade for trade in positions if trade.profit <= 0]
        return len(loosing) >= self.loss_limit

    async def check_balance_level(self) -> bool:
        """Check if the balance level is greater than or equal to the balance level."""
        await self.account.refresh()
        balance_level = (self.account.margin / self.account.balance) * 100
        return balance_level >= self.balance_level
