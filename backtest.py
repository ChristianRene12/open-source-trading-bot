
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
            window = values[i - period + 1:i + 1]
            result.append(sum(window) / period)

    return result


def calculate_statistics(trades, max_drawdown=0.0):
    """Calculate performance statistics
