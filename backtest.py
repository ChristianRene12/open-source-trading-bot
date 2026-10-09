import csv
import argparse
from dataclasses import dataclass


@dataclass
class Trade:
    entry: float
    exit: float
    return_pct: float


def sma(values, period):
    return [
        sum(values[i - period + 1:i + 1]) / period
        if i >= period - 1 else None
        for i in range(len(values))
    ]


def backtest(prices, fast_period=10, slow_period=30):
    if fast_period >= slow_period:
        raise ValueError("Fast period must be smaller than slow period.")

    if len(prices) < slow_period + 1:
        raise ValueError("Not enough price data.")

    fast = sma(prices, fast_period)
    slow = sma(prices, slow_period)

    trades = []
    in_position = False
    entry = 0.0

    equity = 1.0
    peak = 1.0
    max_drawdown = 0.0

    for i in range(1, len(prices)):
        if fast[i] is None or slow[i] is None:
            continue

        crossed_up = (
            fast[i - 1] <= slow[i - 1]
            and fast[i] > slow[i]
        )
        crossed_down = (
            fast[i - 1] >= slow[i - 1]
            and fast[i] < slow[i]
        )

        if not in_position and crossed_up:
            entry = prices[i]
            in_position = True

        elif in_position and crossed_down:
            exit_price = prices[i]
            trade_return = exit_price / entry - 1

            trades.append(
                Trade(entry, exit_price, trade_return * 100)
            )

            equity *= 1 + trade_return
            peak = max(peak, equity)
            max_drawdown = max(
                max_drawdown,
                (peak - equity) / peak
            )
            in_position = False

    wins = sum(t.return_pct > 0 for t in trades)
    total_return = (equity - 1) * 100
    win_rate = wins / len(trades) * 100 if trades else 0

    print("\n--- BACKTEST RESULTS ---")
    print(f"Completed trades: {len(trades)}")
    print(f"Win rate: {win_rate:.2f}%")
    print(f"Total return: {total_return:.2f}%")
    print(f"Maximum drawdown: {max_drawdown * 100:.2f}%")
    print("\nNote: Fees, spread and slippage are not included.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", help="CSV file with a close column")
    parser.add_argument("--fast", type=int, default=10)
    parser.add_argument("--slow", type=int, default=30)
    args = parser.parse_args()

    with open(args.csv_file, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or "close" not in reader.fieldnames:
            raise ValueError("CSV must contain a 'close' column.")

        prices = [float(row["close"]) for row in reader]

    backtest(prices, args.fast, args.slow)


if __name__ == "__main__":
    main()
