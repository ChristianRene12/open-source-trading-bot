```python
import argparse
import csv
from dataclasses import dataclass


@dataclass
class Trade:
    entry: float
    exit: float
    return_pct: float


def sma(values, period):
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

    wins
