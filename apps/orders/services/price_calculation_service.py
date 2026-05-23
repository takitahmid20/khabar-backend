from decimal import Decimal


class PriceCalculationService:
    @staticmethod
    def calculate(items: list[dict]) -> dict:
        subtotal = Decimal("0.00")
        computed_items = []
        for item in items:
            line_total = Decimal(item["unitPrice"]) * item["quantity"] * item["monthMultiplier"]
            subtotal += line_total
            computed_items.append({**item, "lineTotal": line_total})
        return {"subtotal": subtotal, "items": computed_items}
