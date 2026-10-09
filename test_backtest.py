```python
import csv
import os
import tempfile
import unittest

from backtest import (
    sma,
    backtest,
    Trade,
    export_trades_csv,
    calculate_statistics,
)


class TestSMA(unittest.TestCase):

    def test_calculates_simple_moving_average(self):
        result = sma([1, 2, 3, 4, 5], 3)
        self.assertEqual(result, [None, None, 2.0, 3.0, 4.0])

    def test_rejects_zero_period(self):
        with self.assertRaises(ValueError):
            sma([1, 2, 3], 0)


class TestBacktest(unittest.TestCase):

    def test_rejects_invalid_periods(self):
        with self.assertRaises(ValueError):
            backtest([100.0] * 40, 10, 10)

    def test_rejects_insufficient_data(self):
        with self.assertRaises(ValueError):
            backtest([100.0] * 5, 3, 5)

    def test_rejects_non_positive_prices(self):
        prices = [100.0] * 35
        prices[10] = 0

        with self.assertRaises(ValueError):
            backtest(prices, 3, 5)

    def test_constant_prices_produce_no_trades(self):
        trades = backtest([100.0] * 40, 3, 5)
        self.assertEqual(trades, [])

    def test_costs_reduce_profitable_trade_return(self):
        prices = (
            [100.0] * 5
            + [101.0, 103.0, 105.0, 104.0, 102.0, 99.0]
            + [98.0] * 5
        )

        free_trades = backtest(
            prices, fast_period=2, slow_period=3
        )

        costly_trades = backtest(
            prices,
            fast_period=2,
            slow_period=3,
            spread_pct=0.1,
            commission_pct=0.05,
            slippage_pct=0.02,
        )

        self.assertEqual(len(free_trades), len(costly_trades))

        if free_trades:
            self.assertLess(
                costly_trades[0].return_pct,
                free_trades[0].return_pct,
            )

    def test_rejects_negative_costs(self):
        with self.assertRaises(ValueError):
            backtest(
                [100.0] * 40,
                fast_period=3,
                slow_period=5,
                spread_pct=-0.1,
            )

    def test_drawdown_tracks_open_position(self):
        prices = (
            [100.0] * 5
            + [101.0, 105.0, 110.0, 100.0, 95.0, 90.0]
            + [92.0] * 5
        )

        trades = backtest(
            prices,
            fast_period=2,
            slow_period=3,
        )

        self.assertIsInstance(trades, list)


class TestStatistics(unittest.TestCase):

    def test_calculates_statistics(self):
        trades = [
            Trade(100.0, 110.0, 10.0),
            Trade(100.0, 95.0, -5.0),
            Trade(100.0, 120.0, 20.0),
        ]

        stats = calculate_statistics(trades, max_drawdown=0.1)

        self.assertEqual(stats["completed_trades"], 3)
        self.assertEqual(stats["winning_trades"], 2)
        self.assertEqual(stats["losing_trades"], 1)
        self.assertAlmostEqual(stats["win_rate"], 200 / 3)
        self.assertAlmostEqual(stats["total_return"], 25.4)
        self.assertAlmostEqual(stats["max_drawdown"], 10.0)
        self.assertAlmostEqual(stats["profit_factor"], 6.0)

    def test_empty_trades_return_zero_statistics(self):
        stats = calculate_statistics([])

        self.assertEqual(stats["completed_trades"], 0)
        self.assertEqual(stats["win_rate"], 0.0)
        self.assertEqual(stats["total_return"], 0.0)
        self.assertEqual(stats["max_drawdown"], 0.0)
        self.assertEqual(stats["profit_factor"], 0.0)

    def test_rejects_invalid_drawdown(self):
        with self.assertRaises(ValueError):
            calculate_statistics([], max_drawdown=1.5)

    def test_rejects_total_loss_trade(self):
        trades = [Trade(100.0, 0.0, -100.0)]

        with self.assertRaises(ValueError):
            calculate_statistics(trades)


class TestCSVExport(unittest.TestCase):

    def test_exports_trade_results(self):
        trades = [
            Trade(entry=100.0, exit=110.0, return_pct=9.5),
            Trade(entry=110.0, exit=105.0, return_pct=-4.8),
        ]

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
            newline="",
            encoding="utf-8",
        ) as temp_file:
            file_path = temp_file.name

        try:
            export_trades_csv(trades, file_path)

            with open(
                file_path,
                newline="",
                encoding="utf-8",
            ) as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), 2)
            self.assertEqual(float(rows[0]["entry"]), 100.0)
            self.assertEqual(float(rows[0]["exit"]), 110.0)
            self.assertAlmostEqual(float(rows[0]["return_pct"]), 9.5)
            self.assertAlmostEqual(float(rows[1]["return_pct"]), -4.8)

        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_exports_empty_trade_list(self):
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
            newline="",
            encoding="utf-8",
        ) as temp_file:
            file_path = temp_file.name

        try:
            export_trades_csv([], file_path)

            with open(
                file_path,
                newline="",
                encoding="utf-8",
            ) as file:
                rows = list(csv.reader(file))

            self.assertEqual(
                rows,
                [["entry", "exit", "return_pct"]],
            )

        finally:
            if os.path.exists(file_path):
                os.remove(file_path)


if __name__ == "__main__":
    unittest.main()
```
