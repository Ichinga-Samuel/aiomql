"""Risk Assessment and Management"""
from .account import Account
from .positions import Positions


class RAM:
    account: Account
    risk_to_reward: float
    risk: float
    fixed_amount: float | None
    min_amount: float
    max_amount: float
    loss_limit: int
    open_limit: int

    def __init__(self, **kwargs):
        """Initialize Risk Assessment and Management with the provided keyword arguments.

        Keyword Args:
            risk_to_reward (float): Risk to reward ratio. Defaults to 2
            risk (float): Percentage of capital to risk per trade. Defaults to 1%
            min_amount (float): Minimum amount to risk per trade. Defaults to 0
            max_amount (float): Maximum amount to risk per trade. Defaults to 0
            loss_limit (int): Maximum number of losing positions. Defaults to 1
            open_limit (int): Maximum number of open positions. Defaults to 1
            fixed_amount (float): Fixed amount to risk per trade. Defaults to None
        """
        self.account = Account()
        self.positions = Positions()
        self.risk_to_reward = kwargs.get('risk_to_reward', 2)
        self.risk = kwargs.get('risk', 1)
        self.min_amount = kwargs.get('min_amount', 0)
        self.max_amount = kwargs.get('max_amount', 0)
        self.loss_limit = kwargs.get('loss_limit', 3)
        self.open_limit = kwargs.get('open_limit', 3)
        self.fixed_amount = kwargs.get('fixed_amount', None)

    async def get_amount(self) -> float:
        """Calculate the amount to risk per trade as a percentage of margin_free.

        Returns:
            float: Amount to risk per trade
        """
        if self.fixed_amount:
            return self.fixed_amount
        await self.account.refresh()
        amount = self.account.margin_free * (self.risk/100)
        if self.min_amount and self.max_amount:
            return max(self.min_amount, min(self.max_amount, amount))
        return amount

    async def check_losing_positions(self) -> bool:
        """Check if the number of losing positions is less than the loss limit

        Returns:
            bool: True if the number of losing positions is less than or equal the loss limit
        """
        positions = await self.positions.get_positions()
        loosing = [position for position in positions if position.profit < 0]
        return len(loosing) <= self.loss_limit

    async def check_open_positions(self) -> bool:
        """Check if the number of open positions is less than or equal the loss limit.

        Returns:
            bool: True if the number of open positions is less than the open limit
        """
        positions = await self.positions.get_positions()
        return len(positions) <= self.open_limit
