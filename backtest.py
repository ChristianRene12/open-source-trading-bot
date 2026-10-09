
import argparse
import csv
from dataclasses import dataclass


@dataclass
class Trade:
    entry: float
    exit: float
    return_pct: float


def sma(values, period):
    """Calculate a simple moving average."""
    if period <= 0:
        raise ValueError("Period must be positive.")

    result = []

    for i in range(len(values)):
        if i < period - 1:
            result.append(None)
        else:
            result.append(
                sum(values[i - period + 1:i + 1]) / period
            )

    return result


def calculate_statistics(trades, max_drawdown=0.0):
    """Calculate performance statistics from completed trades."""
    if not 0 <= max_drawdown <= 1:
        raise ValueError("max_drawdown must be between 0 and 1.")

    wins = sum(trade.return_pct > 0 for trade in trades)
    losses = sum(trade.return_pct < 0 for trade in trades)

    win_rate = wins / len(trades) * 100 if trades else 0.0

    equity = 1.0
    gross_profit = 0.0
    gross_loss = 0.0

    for trade in trades:
        if trade.return_pct <= -100:
            raise ValueError(
                "Trade return cannot be -100% or lower."
            )

        equity *= 1 + trade.return_pct / 100

        if trade.return_pct > 0:
            gross_profit += trade.return_pct
        elif trade.return_pct < 0:
            gross_loss += abs(trade.return_pct)

    if gross_loss > 0:
        profit_factor = gross_profit / gross_loss
    elif gross_profit > 0:
        profit_factor = float("inf")
    else:
        profit_factor = 0.0

    return {
        "completed_trades": len(trades),
        "winning_trades": wins,
        "losing_trades": losses,
        "win_rate": win_rate,
        "total_return": (equity - 1) * 100,
        "max_draw
