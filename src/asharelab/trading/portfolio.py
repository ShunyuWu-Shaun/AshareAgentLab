from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

from asharelab.trading.rules import AShareRules


@dataclass
class Position:
    symbol: str
    name: str = ""
    quantity: int = 0
    available_quantity: int = 0
    avg_cost: float = 0.0
    last_price: float = 0.0
    last_trade_date: str = ""

    @property
    def market_value(self) -> float:
        return self.quantity * self.last_price


@dataclass
class Trade:
    trade_date: str
    side: str
    symbol: str
    quantity: int
    price: float
    fees: float
    reason: str

    @property
    def amount(self) -> float:
        return self.quantity * self.price


@dataclass
class Portfolio:
    cash: float = 100_000.0
    positions: dict[str, Position] = field(default_factory=dict)
    trades: list[Trade] = field(default_factory=list)

    def equity(self) -> float:
        return self.cash + sum(position.market_value for position in self.positions.values())

    def update_prices(self, prices: dict[str, float]) -> None:
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol].last_price = price

    def roll_t_plus_one(self, today: date) -> None:
        today_s = today.isoformat()
        for position in self.positions.values():
            if position.last_trade_date != today_s:
                position.available_quantity = position.quantity

    def buy(
        self,
        symbol: str,
        name: str,
        quantity: int,
        price: float,
        trade_date: date,
        reason: str,
        rules: AShareRules,
    ) -> Trade | None:
        if not rules.is_valid_buy_quantity(quantity):
            return None
        amount = quantity * price
        fees = rules.fees_for("buy", amount)
        if amount + fees > self.cash:
            return None

        position = self.positions.get(symbol, Position(symbol=symbol, name=name))
        total_cost = position.avg_cost * position.quantity + amount + fees
        position.quantity += quantity
        position.available_quantity = 0
        position.avg_cost = total_cost / position.quantity
        position.last_price = price
        position.last_trade_date = trade_date.isoformat()
        self.positions[symbol] = position
        self.cash -= amount + fees

        trade = Trade(trade_date.isoformat(), "buy", symbol, quantity, price, fees, reason)
        self.trades.append(trade)
        return trade

    def sell(
        self,
        symbol: str,
        quantity: int,
        price: float,
        trade_date: date,
        reason: str,
        rules: AShareRules,
    ) -> Trade | None:
        position = self.positions.get(symbol)
        if not position or quantity <= 0 or quantity > position.available_quantity:
            return None
        amount = quantity * price
        fees = rules.fees_for("sell", amount)
        position.quantity -= quantity
        position.available_quantity -= quantity
        position.last_price = price
        if position.quantity == 0:
            del self.positions[symbol]
        self.cash += amount - fees

        trade = Trade(trade_date.isoformat(), "sell", symbol, quantity, price, fees, reason)
        self.trades.append(trade)
        return trade

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, text: str) -> "Portfolio":
        raw = json.loads(text)
        positions = {
            symbol: Position(**payload) for symbol, payload in raw.get("positions", {}).items()
        }
        trades = [Trade(**payload) for payload in raw.get("trades", [])]
        return cls(cash=float(raw.get("cash", 100_000.0)), positions=positions, trades=trades)

    @classmethod
    def load(cls, path: Path, starting_cash: float = 100_000.0) -> "Portfolio":
        if not path.exists():
            return cls(cash=starting_cash)
        return cls.from_json(path.read_text(encoding="utf-8"))

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")

