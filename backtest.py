
import csv
import argparse
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
            window = values[i - period + 1:i + 1]
            result.append(sum(window) / period)

    return result


def backtest(prices, fast_period=10, slow_period=30):
    if not 0 < fast_period < slow_period:
        raise ValueError(
            "Periods must satisfy 0 < fast_period < slow_period."
        )

    if len(prices) < slow_period + 1:
        raise ValueError("Not enough price data.")

    if any(price <= 0 for price in prices):
        raise ValueError("All prices must be positive.")

    fast = sma(prices, fast_period)
    slow = sma(prices, slow_period)

    trades = []
    in_position = False
    entry = None

    equity = 1.0
    peak = 1.0
    max_drawdown = 0.0

    for i in range(1, len(prices)):
        # Both current and previous SMA values must exist.
        if (
            fast[i] is None
            or slow[i] is None
            or fast[i - 1] is None
            or slow[i - 1] is None
        ):
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

            if peak > 0:
                drawdown = (peak - equity) / peak
                max_drawdown = max(max_drawdown, drawdown)

            in_position = False
            entry = None

    # Close any remaining position at the final available price.
    if in_position and entry is not None:
        exit_price = prices[-1]
        trade_return = exit_price / entry - 1

        trades.append(
            Trade(entry, exit_price, trade_return * 100)
        )

        equity *= 1 + trade_return
        peak = max(peak, equity)

        if peak > 0:
            drawdown = (peak - equity) / peak
            max_drawdown = max(max_drawdown, drawdown)

    wins = sum(trade.return_pct > 0 for trade in trades)
    losses = sum(trade.return_pct < 0 for trade in trades)

    win_rate = (
        wins / len(trades) * 100
        if trades else 0.0
    )

    total_return = (equity - 1) * 100

    gross_profit = sum(
        trade.return_pct for trade in trades
        if trade.return_pct > 0
    )

    gross_loss = abs(sum(
        trade.return_pct for trade in trades
        if trade.return_pct < 0
    ))

    if gross_loss > 0:
        profit_factor = gross_profit / gross_loss
    elif gross_profit > 0:
        profit_factor = float("inf")
    else:
        profit_factor = 0.0

    print("\n--- BACKTEST RESULTS ---")
    print(f"Completed trades: {len(trades)}")
    print(f"Winning trades: {wins}")
    print(f"Losing trades: {losses}")
    print(f"Win rate: {win_rate:.2f}%")
    print(f"Total return: {total_return:.2f}%")
    print(f"Maximum drawdown: {max_drawdown * 100:.2f}%")

    if profit_factor == float("inf"):
        print("Profit factor: Infinite (no losing trades)")
    else:
        print(f"Profit factor: {profit_factor:.2f}")

    print(
        "\nWARNING: This is a simplified research backtest."
        "\nSpread, fees, slippage, position sizing and realistic"
        "\nexecution are not included. Returns are not a forecast."
    )

    return trades


def main():
    parser = argparse.ArgumentParser(
        description="Backtest a simple moving-average crossover strategy."
    )

    parser.add_argument(
        "csv_file",
        help="CSV file containing a column named 'close'."
    )

    parser.add_argument("--fast", type=int, default=10)
    parser.add_argument("--slow", type=int, default=30)

    args = parser.parse_args()

    if not 0 < args.fast < args.slow:
        parser.error("Periods must satisfy 0 < --fast < --slow.")

    try:
        with open(
            args.csv_file,
            newline="",
            encoding="utf-8-sig"
        ) as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames or "close" not in reader.fieldnames:
                raise ValueError(
                    "CSV must contain a column named 'close'."
                )

            prices = []

            for row_number, row in enumerate(reader, start=2):
                try:
                    price = float(row["close"])
                except (TypeError, ValueError):
                    raise ValueError(
                        f"Invalid close price on CSV row {row_number}."
                    )

                prices.append(price)

        backtest(
            prices,
            fast_period=args.fast,
            slow_period=args.slow
        )

    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
