
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
    direction: str = "long",
) -> PositionPlan:
    """Calculate position size using account risk and stop distance.

    value_per_price_unit must reflect the broker's instrument
    contract specifications and account currency.
    """
    if account_equity <= 0:
        raise ValueError("Account equity must be positive.")

    if not 0 < max_risk_percent <= 100:
        raise ValueError("Maximum risk must be greater than 0 and at most 100%.")

    if not 0 < risk_percent <= max_risk_percent:
        raise ValueError(
            f"Risk must be between 0 and {max_risk_percent}%."
        )

    if entry_price <= 0 or stop_loss <= 0:
        raise ValueError("Entry and stop-loss prices must be positive.")

    if value_per_price_unit <= 0:
        raise ValueError("Value per price unit must be positive.")

    if direction not in ("long", "short"):
        raise ValueError("Direction must be 'long' or 'short'.")

    if direction == "long" and stop_loss >= entry_price:
        raise ValueError("For a long position, stop-loss must be below entry.")

    if direction == "short" and stop_loss <= entry_price:
        raise ValueError("For a short position, stop-loss must be above entry.")

    stop_distance = abs(entry_price - stop_loss)
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


def calculate_risk_reward(
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    direction: str = "long",
) -> float:
    """Return reward-to-risk ratio, e.g. 2.0 means a 1:2 risk/reward."""
    if entry_price <= 0 or stop_loss <= 0 or take_profit <= 0:
        raise ValueError("All prices must be positive.")

    if direction == "long":
        risk = entry_price - stop_loss
        reward = take_profit - entry_price
    elif direction == "short":
        risk = stop_loss - entry_price
        reward = entry_price - take_profit
    else:
        raise ValueError("Direction must be 'long' or 'short'.")

    if risk <= 0:
        raise ValueError("Stop-loss is on the wrong side of entry.")

    if reward <= 0:
        raise ValueError("Take-profit is on the wrong side of entry.")

    return reward / risk


if __name__ == "__main__":
    plan = calculate_position_size(
        account_equity=10_000,
        risk_percent=0.5,
        entry_price=2650.0,
        stop_loss=2640.0,
        value_per_price_unit=1.0,
        direction="long",
    )

    ratio = calculate_risk_reward(
        entry_price=2650.0,
        stop_loss=2640.0,
        take_profit=2670.0,
        direction="long",
    )

    print("Example position plan")
    print(f"Account equity: {plan.account_equity:.2f}")
    print(f"Risk amount: {plan.risk_amount:.2f}")
    print(f"Stop distance: {plan.stop_distance:.2f}")
    print(f"Calculated position size: {plan.position_size:.4f}")
    print(f"Reward-to-risk ratio: 1:{ratio:.2f}")
    print("Verify broker contract specifications before trading.")
