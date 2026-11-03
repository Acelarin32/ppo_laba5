from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Order:
    customer: str
    items: list[dict]
    declared_total: Decimal

    @property
    def total(self) -> Decimal:
        return sum((item["price"] * item["quantity"] for item in self.items), Decimal("0.00"))
