
import unittest

from risk_management import calculate_position_size


class TestRiskManagement(unittest.TestCase):

    def test_calculates_position_size(self):
        plan = calculate_position_size(
            account_equity=10_000,
            risk_percent=0.5,
            entry_price=2650,
            stop_loss=2640,
            value_per_price_unit=1.0,
        )

        self.assertAlmostEqual(plan.risk_amount, 50.0)
        self.assertAlmostEqual(plan.stop_distance, 10.0)
        self.assertAlmostEqual(plan.position_size, 5.0)

    def test_short_trade_stop_distance(self):
        plan = calculate_position_size(
            account_equity=10_000,
            risk_percent=1.0,
            entry_price=2640,
            stop_loss=2650,
            value_per_price_unit=1.0,
        )

        self.assertAlmostEqual(plan.stop_distance, 10.0)
        self.assertAlmostEqual(plan.risk_amount, 100.0)

    def test_rejects_zero_equity(self):
        with self.assertRaises(ValueError):
            calculate_position_size(
                0, 0.5, 2650, 2640
            )

    def test_rejects_excessive_risk(self):
        with self.assertRaises(ValueError):
            calculate_position_size(
                10_000, 2.0, 2650, 2640
            )

    def test_rejects_equal_entry_and_stop(self):
        with self.assertRaises(ValueError):
            calculate_position_size(
                10_000, 0.5, 2650, 2650
            )

    def test_rejects_negative_risk(self):
        with self.assertRaises(ValueError):
            calculate_position_size(
                10_000, -0.5, 2650, 2640
            )


if __name__ == "__main__":
    unittest.main()

