"""Comprehensive tests for the position_tracking_functions module.

Tests cover:
- exit_at_profit function (tp/sl conditions, position closing)
- extend_take_profit function (TP extension, percentage checks)
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from aiomql.contrib.trackers.position_tracking_functions import exit_at_profit, extend_take_profit


class TestExitAtProfit:
    """Tests for exit_at_profit function."""

    async def test_exit_at_profit_closes_at_tp(self):
        """Test position closes when profit reaches take profit."""
        mock_position = MagicMock()
        mock_position.profit = 100.0
        
        mock_pos = MagicMock()
        mock_pos.symbol = MagicMock()
        mock_pos.symbol.name = "EURUSD"
        mock_pos.ticket = 12345
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.close_position = AsyncMock(return_value=(True, MagicMock()))
        
        await exit_at_profit(mock_pos, tp=50.0)
        
        mock_pos.close_position.assert_called_once()

    async def test_exit_at_profit_closes_at_sl(self):
        """Test position closes when profit falls to stop loss."""
        mock_position = MagicMock()
        mock_position.profit = -50.0
        
        mock_pos = MagicMock()
        mock_pos.symbol = MagicMock()
        mock_pos.symbol.name = "EURUSD"
        mock_pos.ticket = 12345
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.close_position = AsyncMock(return_value=(True, MagicMock()))
        
        await exit_at_profit(mock_pos, sl=-30.0)
        
        mock_pos.close_position.assert_called_once()

    async def test_exit_at_profit_does_not_close_when_between_tp_sl(self):
        """Test position stays open when profit is between TP and SL."""
        mock_position = MagicMock()
        mock_position.profit = 25.0
        
        mock_pos = MagicMock()
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.close_position = AsyncMock()
        
        await exit_at_profit(mock_pos, tp=50.0, sl=-30.0)
        
        mock_pos.close_position.assert_not_called()

    async def test_exit_at_profit_does_nothing_when_closed(self):
        """Test no action when position is already closed."""
        mock_pos = MagicMock()
        mock_pos.update_position = AsyncMock(return_value=False)
        mock_pos.close_position = AsyncMock()
        
        await exit_at_profit(mock_pos, tp=50.0)
        
        mock_pos.close_position.assert_not_called()

    async def test_exit_at_profit_logs_warning_on_close_failure(self):
        """Test warning is logged when close fails."""
        mock_position = MagicMock()
        mock_position.profit = 100.0
        
        mock_result = MagicMock()
        mock_result.comment = "Market closed"
        
        mock_pos = MagicMock()
        mock_pos.symbol = MagicMock()
        mock_pos.symbol.name = "EURUSD"
        mock_pos.ticket = 12345
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.close_position = AsyncMock(return_value=(False, mock_result))
        
        with patch("aiomql.contrib.trackers.position_tracking_functions.logger") as mock_logger:
            await exit_at_profit(mock_pos, tp=50.0)
            mock_logger.warning.assert_called_once()

    async def test_exit_at_profit_exact_tp_value(self):
        """Test position closes when profit equals exactly TP."""
        mock_position = MagicMock()
        mock_position.profit = 50.0  # Exactly at TP
        
        mock_pos = MagicMock()
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.close_position = AsyncMock(return_value=(True, MagicMock()))
        
        await exit_at_profit(mock_pos, tp=50.0)
        
        mock_pos.close_position.assert_called_once()

    async def test_exit_at_profit_exact_sl_value(self):
        """Test position closes when profit equals exactly SL."""
        mock_position = MagicMock()
        mock_position.profit = -30.0  # Exactly at SL
        
        mock_pos = MagicMock()
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.close_position = AsyncMock(return_value=(True, MagicMock()))
        
        await exit_at_profit(mock_pos, sl=-30.0)
        
        mock_pos.close_position.assert_called_once()

    async def test_exit_at_profit_only_tp_provided(self):
        """Test works with only tp provided."""
        mock_position = MagicMock()
        mock_position.profit = 25.0
        
        mock_pos = MagicMock()
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.close_position = AsyncMock()
        
        await exit_at_profit(mock_pos, tp=50.0)
        
        mock_pos.close_position.assert_not_called()

    async def test_exit_at_profit_only_sl_provided(self):
        """Test works with only sl provided."""
        mock_position = MagicMock()
        mock_position.profit = 25.0
        
        mock_pos = MagicMock()
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.close_position = AsyncMock()
        
        await exit_at_profit(mock_pos, sl=-30.0)
        
        mock_pos.close_position.assert_not_called()


class TestExtendTakeProfit:
    """Tests for extend_take_profit function."""

    async def test_extend_take_profit_does_nothing_when_closed(self):
        """Test no action when position is closed."""
        mock_pos = MagicMock()
        mock_pos.update_position = AsyncMock(return_value=False)
        mock_pos.modify_stops = AsyncMock()
        
        await extend_take_profit(mock_pos)
        
        mock_pos.modify_stops.assert_not_called()

    async def test_extend_take_profit_does_nothing_when_loss(self):
        """Test no action when position is in loss."""
        mock_position = MagicMock()
        mock_position.profit = -10.0
        
        mock_pos = MagicMock()
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.modify_stops = AsyncMock()
        
        await extend_take_profit(mock_pos)
        
        mock_pos.modify_stops.assert_not_called()

    async def test_extend_take_profit_extends_when_threshold_reached(self):
        """Test TP is extended when percentage threshold reached."""
        mock_position = MagicMock()
        mock_position.profit = 50.0
        mock_position.price_open = 1.1000
        mock_position.tp = 1.1100
        mock_position.price_current = 1.1085  # 85% of distance to TP
        mock_position.symbol = "EURUSD"
        mock_position.ticket = 12345
        
        mock_pos = MagicMock()
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.modify_stops = AsyncMock(return_value=(True, MagicMock()))
        
        with patch("aiomql.contrib.trackers.position_tracking_functions.get_price_in_range_pct",
                   return_value=85):  # Above 80% threshold
            with patch("aiomql.contrib.trackers.position_tracking_functions.extend_interval_by_percentage",
                       return_value=1.1120):
                await extend_take_profit(mock_pos, increase=20, start=80)
                
                mock_pos.modify_stops.assert_called_once_with(tp=1.1120, use_stop_levels=True)

    async def test_extend_take_profit_does_not_extend_below_threshold(self):
        """Test TP is not extended when below percentage threshold."""
        mock_position = MagicMock()
        mock_position.profit = 30.0
        mock_position.price_open = 1.1000
        mock_position.tp = 1.1100
        mock_position.price_current = 1.1050  # 50% of distance to TP
        
        mock_pos = MagicMock()
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.modify_stops = AsyncMock()
        
        with patch("aiomql.contrib.trackers.position_tracking_functions.get_price_in_range_pct",
                   return_value=50):  # Below 80% threshold
            await extend_take_profit(mock_pos, increase=20, start=80)
            
            mock_pos.modify_stops.assert_not_called()

    async def test_extend_take_profit_logs_success(self):
        """Test info is logged on successful extension."""
        mock_position = MagicMock()
        mock_position.profit = 50.0
        mock_position.price_open = 1.1000
        mock_position.tp = 1.1100
        mock_position.price_current = 1.1085
        mock_position.symbol = "EURUSD"
        mock_position.ticket = 12345
        
        mock_pos = MagicMock()
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.modify_stops = AsyncMock(return_value=(True, MagicMock()))
        
        with patch("aiomql.contrib.trackers.position_tracking_functions.get_price_in_range_pct",
                   return_value=85):
            with patch("aiomql.contrib.trackers.position_tracking_functions.extend_interval_by_percentage",
                       return_value=1.1120):
                with patch("aiomql.contrib.trackers.position_tracking_functions.logger") as mock_logger:
                    await extend_take_profit(mock_pos)
                    mock_logger.info.assert_called_once()

    async def test_extend_take_profit_logs_warning_on_failure(self):
        """Test warning is logged when modification fails."""
        mock_position = MagicMock()
        mock_position.profit = 50.0
        mock_position.price_open = 1.1000
        mock_position.tp = 1.1100
        mock_position.price_current = 1.1085
        mock_position.symbol = "EURUSD"
        mock_position.ticket = 12345
        
        mock_result = MagicMock()
        mock_result.comment = "Invalid stops"
        
        mock_pos = MagicMock()
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.modify_stops = AsyncMock(return_value=(False, mock_result))
        
        with patch("aiomql.contrib.trackers.position_tracking_functions.get_price_in_range_pct",
                   return_value=85):
            with patch("aiomql.contrib.trackers.position_tracking_functions.extend_interval_by_percentage",
                       return_value=1.1120):
                with patch("aiomql.contrib.trackers.position_tracking_functions.logger") as mock_logger:
                    await extend_take_profit(mock_pos)
                    mock_logger.warning.assert_called_once()

    async def test_extend_take_profit_uses_custom_params(self):
        """Test extend_take_profit uses custom increase and start values."""
        mock_position = MagicMock()
        mock_position.profit = 50.0
        mock_position.price_open = 1.1000
        mock_position.tp = 1.1100
        mock_position.price_current = 1.1070  # 70% of distance
        mock_position.symbol = "EURUSD"
        mock_position.ticket = 12345
        
        mock_pos = MagicMock()
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.modify_stops = AsyncMock(return_value=(True, MagicMock()))
        
        with patch("aiomql.contrib.trackers.position_tracking_functions.get_price_in_range_pct",
                   return_value=70):  # Matches start=70 threshold
            with patch("aiomql.contrib.trackers.position_tracking_functions.extend_interval_by_percentage",
                       return_value=1.1150):
                await extend_take_profit(mock_pos, increase=50, start=70)
                
                mock_pos.modify_stops.assert_called_once_with(tp=1.1150, use_stop_levels=True)

    async def test_extend_take_profit_respects_use_stop_levels(self):
        """Test extend_take_profit passes use_stop_levels correctly."""
        mock_position = MagicMock()
        mock_position.profit = 50.0
        mock_position.price_open = 1.1000
        mock_position.tp = 1.1100
        mock_position.price_current = 1.1085
        mock_position.symbol = "EURUSD"
        mock_position.ticket = 12345
        
        mock_pos = MagicMock()
        mock_pos.position = mock_position
        mock_pos.update_position = AsyncMock(return_value=True)
        mock_pos.modify_stops = AsyncMock(return_value=(True, MagicMock()))
        
        with patch("aiomql.contrib.trackers.position_tracking_functions.get_price_in_range_pct",
                   return_value=85):
            with patch("aiomql.contrib.trackers.position_tracking_functions.extend_interval_by_percentage",
                       return_value=1.1120):
                await extend_take_profit(mock_pos, use_stop_levels=False)
                
                mock_pos.modify_stops.assert_called_once_with(tp=1.1120, use_stop_levels=False)
