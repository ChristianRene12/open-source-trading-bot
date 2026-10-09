
import unittest
import tempfile
import os
import csv

from backtest import sma, backtest, Trade


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
        prices = [100.0] * 40
        trades = backtest(prices, 3, 5)

        self.assertEqual(trades, [])

    def test_costs_reduce_profitable_trade_return(self):
        prices = (
            [100.0] * 5
            + [101.0, 103.0, 105.0, 104.0, 102.0, 99.0]
            + [98.0] * 5
        )

        free_trades = backtest(
            prices,
            fast_period=2,
            slow_period=3,
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

    def test_trade_dataclass_stores_values(self):
        trade = Trade(
            entry=100.0,
            exit=110.0,
            return_pct=10.0,
        )

        self.assertEqual(trade.entry, 100.0)
        self.assertEqual(trade.exit, 110.0)
        self.assertEqual(trade.return_pct, 10.0)


class TestCSVExportPreparation(unittest.TestCase):

    def test_csv_can_store_trade_results(self):
        trade = Trade(
            entry=100.0,
            exit=110.0,
            return_pct=9.5,
        )

        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            encoding="utf-8",
            suffix=".csv",
            delete=False,
        ) as temp_file:
            file_path = temp_file.name

            writer = csv.writer(temp_file)
            writer.writerow(["entry", "exit", "return_pct"])
            writer.writerow([
                trade.entry,
                trade.exit,
                trade.return_pct,
            ])

        try:
            with open(
                file_path,
                newline="",
                encoding="utf-8",
            ) as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), 1)
            self.assertEqual(float(rows[0]["entry"]), 100.0)
            self.assertEqual(float(rows[0]["exit"]), 110.0)
            self.assertEqual(float(rows[0]["return_pct"]), 9.5)

        finally:
            os.remove(file_path)


if __name__ == "__main__":
    unittest.main()
