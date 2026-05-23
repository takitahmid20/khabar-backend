from decimal import Decimal


class CheckoutService:
    @staticmethod
    def calculate_summary(items):
        subtotal = Decimal("0.00")
        item_list = []
        for item in items:
            line_total = item.unit_price * item.quantity * item.month_multiplier
            subtotal += line_total
            item_list.append({
                "dishId": str(item.dish_id),
                "dishName": item.dish_name,
                "mealSlot": item.meal_slot,
                "dayLabel": item.day_label,
                "planType": item.plan_type,
                "quantity": item.quantity,
                "unitPrice": str(item.unit_price),
                "monthMultiplier": item.month_multiplier,
                "lineTotal": str(line_total),
            })
        return {
            "items": item_list,
            "subtotal": subtotal,
            "promoCode": "",
            "promoDiscount": Decimal("0.00"),
            "deliveryFee": Decimal("0.00"),
            "platformFee": Decimal("0.00"),
            "total": subtotal,
            "currency": "BDT",
        }
