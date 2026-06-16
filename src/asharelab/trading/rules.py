from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeeModel:
    commission_rate: float = 0.0003
    min_commission: float = 5.0
    transfer_rate: float = 0.00001
    stamp_duty_rate: float = 0.0005


@dataclass(frozen=True)
class AShareRules:
    """A compact rule set for paper trading common A-share stocks.

    Defaults model main-board stocks: T+1 sell availability, 100-share buy lots,
    0.01 RMB tick size, and 10% daily price limits.
    """

    lot_size: int = 100
    tick_size: float = 0.01
    main_board_limit: float = 0.10
    st_limit: float = 0.05
    growth_board_limit: float = 0.20
    fees: FeeModel = FeeModel()

    def buy_lot_quantity(self, cash: float, price: float, max_position_value: float) -> int:
        spendable = max(0.0, min(cash, max_position_value))
        gross_lots = int(spendable // (price * self.lot_size))
        return gross_lots * self.lot_size

    def is_valid_buy_quantity(self, quantity: int) -> bool:
        return quantity >= self.lot_size and quantity % self.lot_size == 0

    def price_limit_bounds(
        self,
        previous_close: float,
        *,
        is_st: bool = False,
        board: str = "main",
    ) -> tuple[float, float]:
        if previous_close <= 0:
            raise ValueError("previous_close must be positive")
        if is_st:
            limit = self.st_limit
        elif board in {"star", "chinext"}:
            limit = self.growth_board_limit
        else:
            limit = self.main_board_limit
        lower = round(previous_close * (1 - limit), 2)
        upper = round(previous_close * (1 + limit), 2)
        return lower, upper

    def within_price_limit(
        self,
        price: float,
        previous_close: float,
        *,
        is_st: bool = False,
        board: str = "main",
    ) -> bool:
        lower, upper = self.price_limit_bounds(previous_close, is_st=is_st, board=board)
        return lower <= price <= upper

    def fees_for(self, side: str, amount: float) -> float:
        commission = max(self.fees.min_commission, amount * self.fees.commission_rate)
        transfer = amount * self.fees.transfer_rate
        stamp = amount * self.fees.stamp_duty_rate if side == "sell" else 0.0
        return round(commission + transfer + stamp, 2)
