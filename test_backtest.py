
import unittest

from backtest import sma, backtest


class TestSMA(unittest.TestCase):

    def test_calculates_simple_moving_average(self):
        result = sma([1, 2, 3, 4, 5], 3)

        self.assertEqual(
            result,
            [None, None, 2.0, 3.0, 4.0]
        )

    def test_rejects_zero_period(self):
        with self.assertRaises(ValueError):
            sma([1, 2, 3], 0)


class TestBacktest(unittest.TestCase):

    def test_rejects_invalid_periods(self):
        with self.assertRaises(ValueError):
            backtest([100.0] * 40, 10, 10)

    def test_rejects_insufficient_data(self):
        with self.assertRaises(ValueError):
            backtest([100.0] * 10, 3, 5)

    def test_rejects_non_positive_prices(self):
        prices = [100.0] * 35
        prices[10] = 0

        with self.assertRaises(ValueError):
            backtest(prices, 3, 5)

    def test_constant_prices_produce_no_trades(self):
        prices = [100.0] * 40

        trades = backtest(prices, 3, 5)

        self.assertEqual(trades, [])


if __name__ == "__main__":
    unittest.main()
