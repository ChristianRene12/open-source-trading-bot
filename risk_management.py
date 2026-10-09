
"""Risk management utilities for an experimental trading research toolkit."""

from dataclasses import dataclass


@dataclass
class PositionPlan:
    account_equity: float
    risk_amount: float
    stop_distance: float
    position_size: float


def calculate_position_size(
    account_equity: float,
    risk_percent: float,
    entry_price: float,
    stop_loss: float,
    value_per_price_unit: float = 1.0,
    max_risk_percent: float = 1.0,
) -> PositionPlan:
    """Calculate position size from account risk and stop distance.

    value_per_price_unit is the account-currency value of a 1.0
    price move for one unit of position size. This must be configured
    correctly for the instrument and broker.
    """
    if account_equity <= 0:
        raise ValueError("Account equity must be positive.")

    if not 0 < risk_percent <= max_risk_percent:
        raise ValueError(
            f"Risk must be between 0 and {max_risk_percent}%."
        )

    if entry_price <= 0 or stop_loss <= 0:
        raise ValueError("Entry and stop-loss prices must be positive.")

    if value_per_price_unit <= 0:
        raise ValueError("Value per price unit must be positive.")

    stop_distance = abs(entry_price - stop_loss)

    if stop_distance == 0:
        raise ValueError("Stop-loss must differ from entry price.")

    risk_amount = account_equity * risk_percent / 100
    position_size = risk_amount / (
        stop_distance * value_per_price_unit
    )

    return PositionPlan(
        account_equity=account_equity,
        risk_amount=risk_amount,
        stop_distance=stop_distance,
        position_size=position_size,
    )


if __name__ == "__main__":
    plan = calculate_position_size(
        account_equity=10_000,
        risk_percent=0.5,
        entry_price=2650.0,
        stop_loss=2640.0,
        value_per_price_unit=1.0,
    )

    print("Example position plan")
    print(f"Account equity: {plan.account_equity:.2f}")
    print(f"Risk amount: {plan.risk_amount:.2f}")
    print(f"Stop distance: {plan.stop_distance:.2f}")
    print(f"Calculated position size: {plan.position_size:.4f}")
    print("Verify instrument contract specifications before trading.")

