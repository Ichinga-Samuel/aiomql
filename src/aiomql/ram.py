"""Risk Assessment and Management"""
from .account import Account
from .positions import Positions


class RAM:
    account: Account
    risk_to_reward: float
    risk: float
    min_amount: float = 0
    max_amount: float = 0
    loss_limit: int = 3
    open_limit: int = 5

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
        """Calculate the amount to risk per trade as a percentage of margin_free.

        Returns:
            float: Amount to risk per trade
        """
        await self.account.refresh()
        amount = self.account.margin_free * self.risk
        if self.min_amount and self.max_amount:
            return max(self.min_amount, min(self.max_amount, amount))
        return amount

    async def check_losing_positions(self) -> bool:
        """Check if the number of losing positions is greater than or equal the loss limit

        Returns:
            bool: True if the number of losing positions is less than the loss limit
        """
        positions = await Positions().get_positions()
        loosing = [position for position in positions if position.profit < 0]
        return len(loosing) < self.loss_limit

    async def check_open_positions(self) -> bool:
        """Check if the number of open positions is greater than or equal the loss limit.

        Returns:
            bool: True if the number of open positions is less than the open limit
        """
        positions = await Positions().get_positions()
        return len(positions) < self.open_limit
