import argparse
import copy
import json
from importlib.metadata import version
from pathlib import Path

from marshmallow import EXCLUDE, ValidationError

from .schemas import OrderSchema


def main():
    parser = argparse.ArgumentParser(description="Marshmallow 4.0.1 architecture demo")
    parser.add_argument("--case", choices=["valid", "field-error", "total-error", "unknown"], default="valid")
    parser.add_argument("--file", type=Path, help="Load your own JSON file")
    parser.add_argument("--exclude-unknown", action="store_true")
    parser.add_argument("--trace", action="store_true", help="Show hooks and actual library call path")
    args = parser.parse_args()
    if version("marshmallow") != "4.0.1":
        parser.error("Use marshmallow==4.0.1 for reproducible internals")
    data = json.loads(args.file.read_text(encoding="utf-8")) if args.file else {
        "customer": "  STUDENT@example.org  ",
        "items": [{"sku": "BOOK", "quantity": 2, "price": "12.50"}],
        "declared_total": "25.00",
    }
    if not args.file:
        if args.case == "field-error":
            data["customer"] = "invalid-email"
            data["items"][0]["quantity"] = 0
        elif args.case == "total-error":
            data["declared_total"] = "20.00"
        elif args.case == "unknown":
            data["debug"] = True
    original = copy.deepcopy(data)
    hooks = []
    schema = OrderSchema(trace=hooks)
    calls = []


    def profiler(frame, event, arg):
        if event != "call":
            return
        module = frame.f_globals.get("__name__", "")
        name = frame.f_code.co_name
        if module.startswith("marshmallow") and name in {
            "load", "_do_load", "_deserialize", "deserialize", "_validate",
            "_invoke_load_processors", "_invoke_field_validators", "_invoke_schema_validators",
            "store_error", "handle_error",
        }:
            owner = type(frame.f_locals["self"]).__name__ if "self" in frame.f_locals else ""
            calls.append(f"{module}.{owner}.{name}")
    import sys
    previous_profiler = sys.getprofile()
    try:
        if args.trace:
            sys.setprofile(profiler)
        kwargs = {"unknown": EXCLUDE} if args.exclude_unknown else {}
        order = schema.load(data, **kwargs)
    except ValidationError as exc:
        sys.setprofile(previous_profiler)
        print("ERRORS:", json.dumps(exc.messages, ensure_ascii=False, indent=2))
        print("Object created: False")
    else:
        sys.setprofile(previous_profiler)
        print("OBJECT:", repr(order))
        print("DUMP:", json.dumps(schema.dump(order), ensure_ascii=False, indent=2))
    finally:
        sys.setprofile(previous_profiler)
    print("Input unchanged:", data == original)
    if args.trace:
        print("\nHOOKS:")
        print("\n".join(hooks))
        print("\nREAL MARSHMALLOW CALLS (during load):")
        print("\n".join(f"{i:02}. {call}" for i, call in enumerate(calls, 1)))


if __name__ == "__main__":
    main()
