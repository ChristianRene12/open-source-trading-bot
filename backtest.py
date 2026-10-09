
import argparse
import csv
import math
from dataclasses import dataclass


def load_prices_csv(file_path):
    """Load and validate closing prices from a CSV file."""
    with open(
        file_path,
        newline="",
        encoding="utf-8-sig",
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
                ) from None

            if not math.isfinite(price) or price <= 0:
                raise ValueError(
                    f"Invalid close price on CSV row {row_number}: "
                    "price must be finite and positive."
                )

            prices.append(price)

    return prices


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
        "max_drawdown": max_drawdown * 100,
        "profit_factor": profit_factor,
    }


def export_trades_csv(trades, file_path):
    """Export completed trades to a CSV file."""
    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["entry", "exit", "return_pct"])

        for trade in trades:
            writer.writerow([
                trade.entry,
                trade.exit,
                trade.return_pct,
            ])


def backtest(
    prices,
    fast_period=10,
    slow_period=30,
    spread_pct=0.0,
    commission_pct=0.0,
    slippage_pct=0.0,
):
    """Backtest a moving-average crossover strategy."""
    if not 0 < fast_period < slow_period:
        raise ValueError(
            "Periods must satisfy 0 < fast_period < slow_period."
        )

    if len(prices) < slow_period + 1:
        raise ValueError("Not enough price data.")

    if any(price <= 0 for price in prices):
        raise ValueError("All prices must be positive.")

    for name, value in (
        ("spread_pct", spread_pct),
        ("commission_pct", commission_pct),
        ("slippage_pct", slippage_pct),
    ):
        if value < 0:
            raise ValueError(f"{name} cannot be negative.")

    cost_per_side = (
        spread_pct / 2 + commission_pct + slippage_pct
    ) / 100

    if cost_per_side >= 1:
        raise ValueError(
            "Total cost per side must be less than 100%."
        )

    fast = sma(prices, fast_period)
    slow = sma(prices, slow_period)

    trades = []
    entry = None
    in_position = False

    equity = 1.0
    peak_equity = 1.0
    max_drawdown = 0.0

    def update_drawdown(current_equity):
        nonlocal peak_equity, max_drawdown

        peak_equity = max(peak_equity, current_equity)

        if peak_equity > 0:
            drawdown = (
                peak_equity - current_equity
            ) / peak_equity
            max_drawdown = max(max_drawdown, drawdown)

    # Calculate signals at bar i and execute at the next close.
    for i in range(1, len(prices) - 1):
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

        execution_price = prices[i + 1]

        if not in_position and crossed_up:
            entry = execution_price
            in_position = True

        elif in_position and crossed_down:
            exit_price = execution_price
            gross_return = exit_price / entry - 1
            net_return = (
                (1 + gross_return)
                * (1 - cost_per_side) ** 2
                - 1
            )

            trades.append(
                Trade(entry, exit_price, net_return * 100)
            )

            equity *= 1 + net_return
            update_drawdown(equity)

            in_position = False
            entry = None

        if in_position and entry is not None:
            unrealized_return = execution_price / entry - 1
            marked_equity = equity * (1 + unrealized_return)
            update_drawdown(marked_equity)
        else:
            update_drawdown(equity)

    # Close any remaining position at the last available price.
    if in_position and entry is not None:
        exit_price = prices[-1]
        gross_return = exit_price / entry - 1
        net_return = (
            (1 + gross_return)
            * (1 - cost_per_side) ** 2
            - 1
        )

        trades.append(
            Trade(entry, exit_price, net_return * 100)
        )

        equity *= 1 + net_return
        update_drawdown(equity)

    stats = calculate_statistics(trades, max_drawdown)

    print("\n--- BACKTEST RESULTS ---")
    print(f"Completed trades: {stats['completed_trades']}")
    print(f"Winning trades: {stats['winning_trades']}")
    print(f"Losing trades: {stats['losing_trades']}")
    print(f"Win rate: {stats['win_rate']:.2f}%")
    print(f"Total return: {stats['total_return']:.2f}%")
    print(f"Maximum drawdown: {stats['max_drawdown']:.2f}%")

    if stats["profit_factor"] == float("inf"):
        print("Profit factor: Infinite (no losing trades)")
    else:
        print(f"Profit factor: {stats['profit_factor']:.2f}")

    print(
        "\nCosts are simplified percentage estimates."
        "\nResults exclude position sizing and financing."
        "\nThis is research software, not a prediction of returns."
    )

    return trades


def main():
    parser = argparse.ArgumentParser(
        description="Backtest a moving-average crossover strategy."
    )

    parser.add_argument("csv_file", help="CSV file with a close column")
    parser.add_argument("--fast", type=int, default=10)
    parser.add_argument("--slow", type=int, default=30)
    parser.add_argument("--spread-pct", type=float, default=0.0)
    parser.add_argument("--commission-pct", type=float, default=0.0)
    parser.add_argument("--slippage-pct", type=float, default=0.0)
    parser.add_argument(
        "--export-csv",
        help="Optional path to export completed trades",
    )

    args = parser.parse_args()

    if not 0 < args.fast < args.slow:
        parser.error("Periods must satisfy 0 < --fast < --slow.")

    if min(
        args.spread_pct,
        args.commission_pct,
        args.slippage_pct,
    ) < 0:
        parser.error("Cost percentages cannot be negative.")

    try:
        with open(
            args.csv_file,
            newline="",
            encoding="utf-8-sig",
        ) as file:
            reader = csv.DictReader(file)

            if (
                not reader.fieldnames
                or "close" not in reader.fieldnames
            ):
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

        trades = backtest(
            prices,
            fast_period=args.fast,
            slow_period=args.slow,
            spread_pct=args.spread_pct,
            commission_pct=args.commission_pct,
            slippage_pct=args.slippage_pct,
        )

        if args.export_csv:
            export_trades_csv(trades, args.export_csv)
            print(f"Trade log exported to: {args.export_csv}")

    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
