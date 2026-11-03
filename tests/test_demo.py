import copy
import unittest
from decimal import Decimal

from marshmallow import EXCLUDE, ValidationError

from order_demo.models import Order
from order_demo.schemas import Money, OrderSchema


def payload():
    return {"customer": "  STUDENT@example.org ", "items": [{"sku": "BOOK", "quantity": 2, "price": "12.50"}], "declared_total": "25.00"}


class DemoTests(unittest.TestCase):
    def test_load_hooks_and_dump_roundtrip(self):
        data = payload()
        before = copy.deepcopy(data)
        trace = []
        schema = OrderSchema(trace=trace)
        order = schema.load(data)
        self.assertIsInstance(order, Order)
        self.assertEqual(order.customer, "student@example.org")
        self.assertEqual(order.total, Decimal("25.00"))
        self.assertEqual(trace, ["pre_load: normalize", "validates_schema: check_total", "post_load: make_order"])
        self.assertEqual(schema.load(schema.dump(order)), order)
        self.assertEqual(data, before)

    def test_nested_errors_are_aggregated_and_later_hooks_skipped(self):
        data = payload()
        data["customer"] = "bad"
        data["items"][0]["quantity"] = 0
        trace = []
        with self.assertRaises(ValidationError) as error:
            OrderSchema(trace=trace).load(data)
        self.assertIn("customer", error.exception.messages)
        self.assertIn("quantity", error.exception.messages["items"][0])
        self.assertEqual(trace, ["pre_load: normalize"])

    def test_schema_error_prevents_object_creation(self):
        data = payload()
        data["declared_total"] = "1.00"
        trace = []
        with self.assertRaises(ValidationError) as error:
            OrderSchema(trace=trace).load(data)
        self.assertEqual(error.exception.messages, {"declared_total": ["Expected 25.00."]})
        self.assertEqual(len(trace), 2)

    def test_unknown_policy(self):
        data = {**payload(), "extra": True}
        with self.assertRaises(ValidationError):
            OrderSchema().load(data)
        self.assertIsInstance(OrderSchema().load(data, unknown=EXCLUDE), Order)

    def test_missing_null_and_empty_list(self):
        for key, value in [("items", []), ("customer", None), ("declared_total", None)]:
            with self.subTest(key=key), self.assertRaises(ValidationError):
                OrderSchema().load({**payload(), key: value})
        data = payload()
        del data["customer"]
        with self.assertRaises(ValidationError):
            OrderSchema().load(data)

    def test_money_boundaries(self):
        for value in [True, 1.2, "NaN", "Infinity", "-1", "1.001", "oops", "1e100"]:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                Money().deserialize(value)
        self.assertEqual(Money().deserialize("0"), Decimal("0.00"))
        self.assertEqual(Money().deserialize("12.500"), Decimal("12.50"))

    def test_fields_are_bound_to_separate_schema_instances(self):
        first, second = OrderSchema(), OrderSchema()
        self.assertIsNot(first.fields["items"], second.fields["items"])
        self.assertIs(first.fields["items"].parent, first)

    def test_dump_does_not_validate(self):
        # dump сериализует уже существующий объект, не подтверждает корректность данных.
        result = OrderSchema().dump({"customer": "not-an-email", "items": [], "declared_total": Decimal("0.00")})
        self.assertEqual(result["customer"], "not-an-email")


if __name__ == "__main__":
    unittest.main()
