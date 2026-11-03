"""Только публичные точки расширения Marshmallow; внутренности видны в дебаггере."""
from decimal import Decimal, InvalidOperation

from marshmallow import RAISE, Schema, ValidationError, fields, post_load, pre_load, validate, validates_schema

from .models import Order


class Money(fields.Field):
    """Строка с суммой или целое число -> Decimal. Без неявного округления."""

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
            raise ValidationError("Use a decimal string or an integer; floats are not accepted.")
        try:
            amount = Decimal(value)
        except (InvalidOperation, ValueError):
            raise ValidationError("Invalid monetary amount.") from None
        if not amount.is_finite() or amount < 0:
            raise ValidationError("Amount must be finite and non-negative.")
        try:
            rounded = amount.quantize(Decimal("0.01"))
        except InvalidOperation:
            raise ValidationError("Amount is too large.") from None
        if amount != rounded:
            raise ValidationError("Amount must have at most two decimal places.")
        return rounded

    def _serialize(self, value, attr, obj, **kwargs):
        return format(value, ".2f")


class ItemSchema(Schema):
    sku = fields.String(required=True, validate=validate.Length(min=1, max=40))
    quantity = fields.Integer(required=True, strict=True, validate=validate.Range(min=1, max=100))
    price = Money(required=True)


class OrderSchema(Schema):
    customer = fields.Email(required=True)
    items = fields.List(fields.Nested(ItemSchema), required=True, validate=validate.Length(min=1, max=20))
    declared_total = Money(required=True)

    class Meta:
        unknown = RAISE

    def __init__(self, *args, trace=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.trace = trace if trace is not None else []

    @pre_load
    def normalize(self, data, **kwargs):
        self.trace.append("pre_load: normalize")
        if not isinstance(data, dict):
            raise ValidationError("Order must be a JSON object.")
        normalized = dict(data)
        if isinstance(normalized.get("customer"), str):
            normalized["customer"] = normalized["customer"].strip().lower()
        return normalized

    @validates_schema
    def check_total(self, data, **kwargs):
        self.trace.append("validates_schema: check_total")
        total = sum((item["price"] * item["quantity"] for item in data["items"]), Decimal("0.00"))
        if total != data["declared_total"]:
            raise ValidationError({"declared_total": [f"Expected {total:.2f}."]})

    @post_load
    def make_order(self, data, **kwargs):
        self.trace.append("post_load: make_order")
        return Order(**data)
