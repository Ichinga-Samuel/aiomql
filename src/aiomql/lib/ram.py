"""Risk Assessment and Management"""
from .account import Account
from .positions import Positions


class RAM:
    account: Account
    risk_to_reward: float
    risk: float
    min_amount: float
    max_amount: float
    loss_limit: int
    open_limit: int

    def __init__(self, **kwargs):
        """Initialize Risk Assessment and Management with the provided keyword arguments.

        Keyword Args:
            risk_to_reward (float): Risk to reward ratio. Defaults to 1
            risk (float): Percentage of capital to risk per trade 0.01 # 1%
            kwargs: extra keyword arguments are set as object attributes
        """
        self.account = Account()
        self.positions = Positions()
        self.risk_to_reward = kwargs.get('risk_to_reward', 1)
        self.risk = kwargs.get('risk', 0.01)
        self.min_amount = kwargs.get('min_amount', 0)
        self.max_amount = kwargs.get('max_amount', 0)
        self.loss_limit = kwargs.get('loss_limit', 1)
        self.open_limit = kwargs.get('open_limit', 1)

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
        """Check if the number of losing positions is greater than the loss limit

        Returns:
            bool: True if the number of losing positions is less than or equal the loss limit
        """
        positions = await self.positions.get_positions()
        loosing = [position for position in positions if position.profit < 0]
        return len(loosing) <= self.loss_limit

    async def check_open_positions(self) -> bool:
        """Check if the number of open positions is greater than or equal the loss limit.

        Returns:
            bool: True if the number of open positions is less than the open limit
        """
        positions = await self.positions.get_positions()
        return len(positions) <= self.open_limit
