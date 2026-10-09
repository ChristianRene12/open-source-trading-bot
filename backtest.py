
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
            result.append(
                sum(values[i - period + 1:i + 1]) / period
            )

    return result


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
        raise ValueError("Total cost per side must be less than 100%.")

    fast = sma(prices, fast_period)
    slow = sma(prices, slow_period)

    trades = []
    entry = None
    in_position = False

    equity = 1.0
    peak = 1.0
    max_drawdown = 0.0

    for i in range(1, len(prices)):
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
            gross_return = exit_price / entry - 1
            net_return = (
                (1 + gross_return) * (1 - cost_per_side) ** 2 - 1
            )

            trades.append(
                Trade(entry, exit_price, net_return * 100)
            )

            equity *= 1 + net_return
            peak = max(peak, equity)

            if peak > 0:
                drawdown = (peak - equity) / peak
                max_drawdown = max(max_drawdown, drawdown)

            in_position = False
            entry = None

    if in_position and entry is not None:
        exit_price = prices[-1]
        gross_return = exit_price / entry - 1
        net_return = (
            (1 + gross_return) * (1 - cost_per_side) ** 2 - 1
        )

        trades.append(
            Trade(entry, exit_price, net_return * 100)
        )

        equity *= 1 + net_return
        peak = max(peak, equity)

        if peak > 0:
            drawdown = (peak - equity) / peak
            max_drawdown = max(max_drawdown, drawdown)

    wins = sum(t.return_pct > 0 for t in trades)
    losses = sum(t.return_pct < 0 for t in trades)
    win_rate = wins / len(trades) * 100 if trades else 0.0
    total_return = (equity - 1) * 100

    gross_profit = sum(
        t.return_pct for t in trades if t.return_pct > 0
    )
    gross_loss = abs(sum(
        t.return_pct for t in trades if t.return_pct < 0
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
