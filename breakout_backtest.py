
import argparse
import csv
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo


UTC = timezone.utc
LONDON = ZoneInfo("Europe/London")
NEW_YORK = ZoneInfo("America/New_York")


def load_bars(path):
    bars = []

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"datetime", "open", "high", "low", "close"}

        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(
                "CSV must contain datetime, open, high, low, close columns."
            )

        for row in reader:
            dt = datetime.fromisoformat(
                row["datetime"].strip().replace("Z", "+00:00")
            )
            if dt.tzinfo is None:
                raise ValueError("Timestamps must include a timezone.")

            bars.append({
                "time": dt.astimezone(UTC),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
            })

    if len(bars) < 50:
        raise ValueError("Not enough candles for the backtest.")

    if any(bars[i]["time"] >= bars[i + 1]["time"]
           for i in range(len(bars) - 1)):
        raise ValueError("Candles must be sorted by timestamp.")

    return bars


def in_trading_session(dt):
    # Local times, automatically adjusted for daylight saving.
    london = dt.astimezone(LONDON).time()
    new_york = dt.astimezone(NEW_YORK).time()

    london_open = time(8, 0) <= london < time(17, 0)
    new_york_open = time(8, 0) <= new_york < time(17, 0)

    return london_open or new_york_open


def calculate_atr(bars, period=14):
    tr = [None] * len(bars)

    for i in range(1, len(bars)):
        current = bars[i]
        previous_close = bars[i - 1]["close"]
        tr[i] = max(
            current["high"] - current["low"],
            abs(current["high"] - previous_close),
            abs(current["low"] - previous_close),
        )

    atr = [None] * len(bars)

    if len(bars) <= period:
        return atr

    # Wilder ATR: seed with the first period of true ranges.
    atr[period] = sum(tr[1:period + 1]) / period

    for i in range(period + 1, len(bars)):
        atr[i] = (
            atr[i - 1] * (period - 1) + tr[i]
        ) / period

    return atr


def run_backtest(
    bars,
    reward_risk=1.5,
    range_period=20,
    atr_period=14,
    atr_multiplier=1.5,
    spread_pct=0.01,
    slippage_pct=0.005,
    commission_pct=0.0,
):
    if reward_risk <= 0 or atr_multiplier <= 0:
        raise ValueError("Reward/risk and ATR multiplier must be positive.")

    if min(spread_pct, slippage_pct, commission_pct) < 0:
        raise ValueError("Costs cannot be negative.")

    atr = calculate_atr(bars, atr_period)
    trades = []
    position = None

    for i in range(max(range_period, atr_period + 1), len(bars)):
        bar = bars[i]

        # If a trade was open before this candle, check its exit first.
        if position is not None:
            stop_hit = (
                bar["low"] <= position["stop"]
                if position["side"] == "long"
                else bar["high"] >= position["stop"]
            )
            target_hit = (
                bar["high"] >= position["target"]
                if position["side"] == "long"
                else bar["low"] <= position["target"]
            )

            # Conservative assumption if stop and target both hit.
            if stop_hit or target_hit:
                if stop_hit:
                    exit_price = position["stop"]
                    reason = "stop"
                else:
                    exit_price = position["target"]
                    reason = "target"

                entry = position["entry"]
                side_sign = 1 if position["side"] == "long" else -1
                gross_pct = side_sign * (exit_price - entry) / entry * 100

                # Approximate round-trip costs as a percentage of price.
                costs_pct = 2 * (spread_pct + slippage_pct) + 2 * commission_pct
                net_pct = gross_pct - costs_pct

                trades.append({
                    "entry_time": position["entry_time"].isoformat(),
                    "exit_time": bar["time"].isoformat(),
                    "side": position["side"],
                    "entry": entry,
                    "exit": exit_price,
                    "reason": reason,
                    "gross_pct": gross_pct,
                    "net_pct": net_pct,
                })
                position = None

            # Do not open a new trade on the same candle as an exit.
            continue

        if not in_trading_session(bar["time"]) or atr[i] is None:
            continue

        # Use only the preceding candles, never the current candle.
        prior = bars[i - range_period:i]
        range_high = max(b["high"] for b in prior)
        range_low = min(b["low"] for b in prior)
        close = bar["close"]

        if close > range_high:
            side = "long"
            entry = close
            stop = entry - atr_multiplier * atr[i]
            risk = entry - stop
            target = entry + reward_risk * risk
        elif close < range_low:
            side = "short"
            entry = close
            stop = entry + atr_multiplier * atr[i]
            risk = stop - entry
            target = entry - reward_risk * risk
        else:
            continue

        position = {
            "side": side,
            "entry": entry,
            "entry_time": bar["time"],
            "stop": stop,
            "target": target,
        }

    # Close any remaining position at the last close.
    if position is not None:
        final = bars[-1]
        entry = position["entry"]
        exit_price = final["close"]
        sign = 1 if position["side"] == "long" else -1
        gross_pct = sign * (exit_price - entry) / entry * 100
        costs_pct = 2 * (spread_pct + slippage_pct) + 2 * commission_pct

        trades.append({
            "entry_time": position["entry_time"].isoformat(),
            "exit_time": final["time"].isoformat(),
            "side": position["side"],
            "entry": entry,
            "exit": exit_price,
            "reason": "end_of_data",
            "gross_pct": gross_pct,
            "net_pct": gross_pct - costs_pct,
        })

    return trades


def report(trades, reward_risk):
    wins = [t["net_pct"] for t in trades if t["net_pct"] > 0]
    losses = [t["net_pct"] for t in trades if t["net_pct"] < 0]

    equity = 1.0
    peak = 1.0
    max_drawdown = 0.0

    for trade in trades:
        equity *= 1 + trade["net_pct"] / 100
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, (peak - equity) / peak)

    total_return = (equity - 1) * 100
    profit_factor = sum(wins) / abs(sum(losses)) if losses else float("inf")
    win_rate = len(wins) / len(trades) * 100 if trades else 0.0

    print(f"\n--- BREAKOUT RESULTS ({reward_risk}R) ---")
    print(f"Completed trades: {len(trades)}")
    print(f"Winning trades: {len(wins)}")
    print(f"Losing trades: {len(losses)}")
    print(f"Win rate: {win_rate:.2f}%")
    print(f"Total return: {total_return:.2f}%")
    print(f"Maximum drawdown: {max_drawdown * 100:.2f}%")
    print(f"Profit factor: {profit_factor:.2f}")


def main():
    parser = argparse.ArgumentParser(
        description="Backtest an XAUUSD breakout strategy."
    )
    parser.add_argument("csv_file")
    parser.add_argument("--spread-pct", type=float, default=0.01)
    parser.add_argument("--slippage-pct", type=float, default=0.005)
    parser.add_argument("--commission-pct", type=float, default=0.0)
    parser.add_argument("--atr-multiplier", type=float, default=1.5)
    parser.add_argument("--export-prefix", default="breakout")
    args = parser.parse_args()

    bars = load_bars(args.csv_file)

    for rr in (1.5, 2.0):
        trades = run_backtest(
            bars,
            reward_risk=rr,
            spread_pct=args.spread_pct,
            slippage_pct=args.slippage_pct,
            commission_pct=args.commission_pct,
            atr_multiplier=args.atr_multiplier,
        )
        report(trades, rr)

        output = f"{args.export_prefix}_{str(rr).replace('.', '_')}R.csv"
        fields = [
            "entry_time", "exit_time", "side", "entry", "exit",
            "reason", "gross_pct", "net_pct",
        ]
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(trades)
        print(f"Trade log exported to: {output}")


if __name__ == "__main__":
    main()

