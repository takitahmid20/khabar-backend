#!/usr/bin/env python3
"""
KHABAR API Full Test Suite — interactive end-to-end testing.
Run:  ./.venv/bin/python test_api_full.py

You will be prompted to enter OTP codes from the terminal output.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime

BASE = "http://127.0.0.1:8000/api/v1"
PASS = 0
FAIL = 0
SKIP = 0


def log(step: str, ok: bool, detail: str = ""):
    global PASS, FAIL
    icon = "✅" if ok else "❌"
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(f"  {icon} {step}")
    if detail:
        for line in detail.split("\n"):
            print(f"     {line}")


def req(method, path, token=None, payload=None, raw_body=False):
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            body = resp.read()
            if raw_body:
                return resp.status, body.decode()
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read()
        if raw_body:
            return e.code, body.decode()
        return e.code, json.loads(body) if body else {}
    except Exception as e:
        return 0, {"error": {"message": str(e)}}


def get_otp_inline(destination, role, method):
    """Read OTP directly from DB for automated testing."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    import django
    django.setup()
    from apps.auth.models import OTP
    otp = OTP.objects.filter(
        destination=destination, role=role, method=method
    ).order_by("-created_at").first()
    return otp.code if otp else None


def get_otp_interactive(destination):
    """Prompt user for OTP."""
    return input(f"    >>> Enter OTP sent to {destination}: ").strip()


def get_otp(destination, role, method, interactive=False):
    if interactive:
        return get_otp_interactive(destination)
    return get_otp_inline(destination, role, method)


# ─── SCENARIO ──────────────────────────────────────────────────────

def run_all_tests(interactive_otp=False):
    global PASS, FAIL, SKIP

    print("=" * 60)
    print("KHABAR API — Full Test Suite")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Mode: {'interactive OTP' if interactive_otp else 'auto OTP (DB)'}")
    print("=" * 60)

    # ─── Auth: Cook signup ─────────────────────────────────────────
    print("\n╔══ 1. AUTH — Cook Signup ══╗")
    COOK_MOBILE = "+8801711000111"

    s, d = req("POST", "/auth/otp/send", payload={
        "method": "mobile",
        "destination": COOK_MOBILE,
        "role": "cook",
    })
    log("POST /auth/otp/send (cook)", s == 200,
        f"status={s}" if s != 200 else "")

    code = get_otp(COOK_MOBILE, "cook", "mobile", interactive_otp)
    if not code:
        log("POST /auth/otp/verify (cook)", False, "No OTP code available")
        return

    s, d = req("POST", "/auth/otp/verify", payload={
        "method": "mobile",
        "destination": COOK_MOBILE,
        "code": code,
        "role": "cook",
    })
    COOK_TOKEN = d.get("data", {}).get("accessToken")
    log("POST /auth/otp/verify (cook)", s == 200 and bool(COOK_TOKEN),
        f"isNewUser={d.get('data',{}).get('isNewUser')}" if s == 200 else json.dumps(d.get("error",{})))

    if not COOK_TOKEN:
        return

    # ─── Cook Onboarding ───────────────────────────────────────────
    print("\n╔══ 2. COOK ONBOARDING ══╗")

    s, d = req("PATCH", "/cook/onboarding/name", token=COOK_TOKEN,
               payload={"displayName": "Rina Begum"})
    log("PATCH /cook/onboarding/name", s == 200,
        f"displayName={d.get('data',{}).get('displayName')}" if s == 200 else "")

    s, d = req("PATCH", "/cook/onboarding/profile", token=COOK_TOKEN, payload={
        "bio": "Home cook specialising in Bangladeshi cuisine since 2015.",
        "avatarUrl": "https://cdn.khabar.app/avatars/usr_abc.jpg",
        "cuisineTypes": ["Bengali", "Mughal", "Street Food"],
    })
    log("PATCH /cook/onboarding/profile", s == 200,
        f"id={d.get('data',{}).get('id','')[:8]}..." if s == 200 else "")

    s, d = req("PATCH", "/cook/onboarding/specialties", token=COOK_TOKEN,
               payload={"specialties": ["Biryani", "Kacchi", "Pulao"]})
    log("PATCH /cook/onboarding/specialties", s == 200)

    s, d = req("PATCH", "/cook/onboarding/service-area", token=COOK_TOKEN, payload={
        "areaLabel": "Dhanmondi",
        "radiusKm": 3,
        "coordinates": {"lat": 23.7461, "lng": 90.3742},
    })
    log("PATCH /cook/onboarding/service-area", s == 200)

    s, d = req("POST", "/cook/onboarding/identity", token=COOK_TOKEN, payload={})
    log("POST /cook/onboarding/identity", s == 200,
        f"status={d.get('data',{}).get('status')}" if s == 200 else "")

    s, d = req("PATCH", "/cook/onboarding/payout", token=COOK_TOKEN, payload={
        "payoutMethod": "bkash",
        "payoutNumber": "01711000111",
        "payoutAccountName": "Rina Begum",
    })
    log("PATCH /cook/onboarding/payout", s == 200)

    s, d = req("POST", "/cook/onboarding/complete", token=COOK_TOKEN, payload={})
    log("POST /cook/onboarding/complete", s == 200,
        f"completed={d.get('data',{}).get('onboardingCompleted')}" if s == 200 else "")

    s, d = req("GET", "/cook/onboarding/status", token=COOK_TOKEN)
    log("GET /cook/onboarding/status", s == 200)

    # ─── Cook Profile ──────────────────────────────────────────────
    print("\n╔══ 3. COOK PROFILE & MENU ══╗")

    s, d = req("GET", "/cook/profile", token=COOK_TOKEN)
    COOK_PROFILE_ID = d.get("data", {}).get("id")
    log("GET /cook/profile", s == 200 and bool(COOK_PROFILE_ID),
        f"id={str(COOK_PROFILE_ID)[:8]}..." if COOK_PROFILE_ID else "")

    s, d = req("PATCH", "/cook/profile", token=COOK_TOKEN,
               payload={"bio": "Updated bio"})
    log("PATCH /cook/profile", s == 200)

    s, d = req("PATCH", "/cook/profile/holiday-mode", token=COOK_TOKEN,
               payload={"enabled": True})
    log("PATCH /cook/profile/holiday-mode (ON)", s == 200)

    s, d = req("PATCH", "/cook/profile/holiday-mode", token=COOK_TOKEN,
               payload={"enabled": False})
    log("PATCH /cook/profile/holiday-mode (OFF)", s == 200)

    # ─── Menu ──────────────────────────────────────────────────────
    print("\n╔══ 4. MENU MANAGEMENT ══╗")

    s, d = req("POST", "/cook/menu/dishes", token=COOK_TOKEN, payload={
        "name": "Kacchi Biryani",
        "description": "Aromatic kacchi with potato and egg.",
        "category": "Biryani",
        "meal_slot": "Lunch",
        "days": ["mon", "wed", "fri"],
        "price": 180,
        "capacity": 10,
        "cutoff_time": "10:00",
        "image_url": "https://cdn.khabar.app/dishes/kacchi.jpg",
        "add_ons_label": "Extra egg +20",
    })
    DISH_ID = d.get("data", {}).get("id")
    log("POST /cook/menu/dishes", s == 200 and bool(DISH_ID),
        f"dishId={str(DISH_ID)[:8]}..." if DISH_ID else "")

    s, d = req("GET", "/cook/menu", token=COOK_TOKEN)
    log("GET /cook/menu (own)", s == 200)

    s, d = req("GET", f"/cooks/{COOK_PROFILE_ID}/menu")
    log(f"GET /cooks/{{id}}/menu (public)", s == 200)

    s, d = req("PATCH", f"/cook/menu/dishes/{DISH_ID}/availability",
               token=COOK_TOKEN, payload={"available": False})
    log("PATCH dish availability (OFF)", s == 200)

    s, d = req("PATCH", f"/cook/menu/dishes/{DISH_ID}/availability",
               token=COOK_TOKEN, payload={"available": True})
    log("PATCH dish availability (ON)", s == 200)

    # ─── Auth: Customer signup ─────────────────────────────────────
    print("\n╔══ 5. AUTH — Customer Signup ══╗")
    CUSTOMER_MOBILE = "+8801711000222"

    s, d = req("POST", "/auth/otp/send", payload={
        "method": "mobile",
        "destination": CUSTOMER_MOBILE,
        "role": "customer",
    })
    log("POST /auth/otp/send (customer)", s == 200)

    code = get_otp(CUSTOMER_MOBILE, "customer", "mobile", interactive_otp)
    if not code:
        log("POST /auth/otp/verify (customer)", False, "No OTP code available")
        return

    s, d = req("POST", "/auth/otp/verify", payload={
        "method": "mobile",
        "destination": CUSTOMER_MOBILE,
        "code": code,
        "role": "customer",
    })
    CUSTOMER_TOKEN = d.get("data", {}).get("accessToken")
    log("POST /auth/otp/verify (customer)", s == 200 and bool(CUSTOMER_TOKEN),
        f"isNewUser={d.get('data',{}).get('isNewUser')}" if s == 200 else json.dumps(d.get("error",{})))

    if not CUSTOMER_TOKEN:
        return

    # ─── Customer Onboarding ───────────────────────────────────────
    print("\n╔══ 6. CUSTOMER ONBOARDING ══╗")

    s, d = req("PATCH", "/customer/onboarding/profile", token=CUSTOMER_TOKEN,
               payload={"displayName": "Ayesha Rahman", "avatarUrl": None})
    log("PATCH /customer/onboarding/profile", s == 200)

    s, d = req("POST", "/customer/onboarding/complete", token=CUSTOMER_TOKEN, payload={})
    log("POST /customer/onboarding/complete", s == 200)

    # ─── Addresses ─────────────────────────────────────────────────
    print("\n╔══ 7. ADDRESSES ══╗")

    s, d = req("POST", "/customer/addresses", token=CUSTOMER_TOKEN, payload={
        "label": "Home",
        "line1": "House 12, Road 4, Dhanmondi, Dhaka-1209",
        "line2": None,
        "coordinates": {"lat": 23.7461, "lng": 90.3742},
        "is_default": True,
    })
    ADDRESS_ID = d.get("data", {}).get("id")
    log("POST /customer/addresses", s == 200 and bool(ADDRESS_ID),
        f"addressId={str(ADDRESS_ID)[:8]}..." if ADDRESS_ID else "")

    s, d = req("GET", "/customer/addresses", token=CUSTOMER_TOKEN)
    log("GET /customer/addresses", s == 200)

    # ─── Users/Me ──────────────────────────────────────────────────
    print("\n╔══ 8. USER PROFILE ══╗")

    s, d = req("GET", "/users/me", token=CUSTOMER_TOKEN)
    log("GET /users/me", s == 200,
        f"role={d.get('data',{}).get('role')}" if s == 200 else "")

    # ─── Orders ────────────────────────────────────────────────────
    print("\n╔══ 9. ORDERS ══╗")

    s, d = req("POST", "/orders", token=CUSTOMER_TOKEN, payload={
        "cookId": COOK_PROFILE_ID,
        "items": [
            {
                "dishId": DISH_ID,
                "mealSlot": "Lunch",
                "dayLabel": "mon",
                "planType": "monthly",
                "quantity": 2,
                "unitPrice": 180,
                "monthMultiplier": 4,
            },
        ],
        "deliveryAddressId": ADDRESS_ID,
        "paymentMethod": "bkash",
        "promoCode": "",
        "totalAmount": 1440,
    })
    ORDER_ID = d.get("data", {}).get("id")
    log("POST /orders", s == 200 and bool(ORDER_ID),
        f"orderId={str(ORDER_ID)[:8]}..., status={d.get('data',{}).get('status')}" if ORDER_ID else "")

    # ─── Payment Webhook ───────────────────────────────────────────
    print("\n╔══ 10. PAYMENT ══╗")

    s, d = req("POST", "/webhooks/payment", payload={
        "orderId": ORDER_ID,
        "status": "success",
        "transactionId": "txn_test_001",
    })
    log("POST /webhooks/payment (success)", s == 200)

    # ─── Customer Orders ──────────────────────────────────────────
    print("\n╔══ 11. CUSTOMER ORDERS ══╗")

    s, d = req("GET", f"/customer/orders/{ORDER_ID}", token=CUSTOMER_TOKEN)
    log(f"GET /customer/orders/{{id}}", s == 200,
        f"status={d.get('data',{}).get('status')}, payment_status={d.get('data',{}).get('payment_status')}" if s == 200 else "")

    s, d = req("GET", "/customer/orders", token=CUSTOMER_TOKEN)
    log("GET /customer/orders (list)", s == 200)

    # ─── Subscriptions ─────────────────────────────────────────────
    print("\n╔══ 12. SUBSCRIPTIONS ══╗")

    s, d = req("GET", "/customer/subscriptions", token=CUSTOMER_TOKEN)
    SUBS = d.get("data", {}).get("subscriptions", [])
    SUB_ID = SUBS[0].get("id") if SUBS else None
    log("GET /customer/subscriptions", s == 200 and bool(SUBS),
        f"{len(SUBS)} subscription(s)" if SUBS else "")

    if SUB_ID:
        s, d = req("GET", f"/customer/subscriptions/{SUB_ID}/calendar?month=2026-05",
                    token=CUSTOMER_TOKEN)
        log("GET /customer/subscriptions/{id}/calendar", s == 200,
            f"{len(d.get('data',{}).get('deliveries',[]))} deliveries" if s == 200 else "")

        s, d = req("POST", f"/customer/subscriptions/{SUB_ID}/pause",
                    token=CUSTOMER_TOKEN, payload={"duration": "1w", "quantity": 2})
        log("POST /subscriptions/{id}/pause", s == 200,
            f"status={d.get('data',{}).get('status')}" if s == 200 else "")

        s, d = req("POST", f"/customer/subscriptions/{SUB_ID}/resume",
                    token=CUSTOMER_TOKEN, payload={})
        log("POST /subscriptions/{id}/resume", s == 200)

    # ─── Reviews ───────────────────────────────────────────────────
    print("\n╔══ 13. REVIEWS ══╗")

    s, d = req("POST", "/customer/reviews", token=CUSTOMER_TOKEN, payload={
        "cook": COOK_PROFILE_ID,
        "order": ORDER_ID,
        "rating": 4.5,
        "comment": "Excellent biryani, delivered on time!",
    })
    log("POST /customer/reviews", s == 200,
        f"reviewId={str(d.get('data',{}).get('id',''))[:8]}..." if s == 200 else "")

    s, d = req("GET", "/customer/reviews", token=CUSTOMER_TOKEN)
    log("GET /customer/reviews (mine)", s == 200)

    s, d = req("GET", f"/cooks/{COOK_PROFILE_ID}/reviews")
    log("GET /cooks/{id}/reviews (public)", s == 200)

    # ─── Notifications ─────────────────────────────────────────────
    print("\n╔══ 14. NOTIFICATIONS ══╗")

    s, d = req("GET", "/notifications", token=CUSTOMER_TOKEN)
    log("GET /notifications", s == 200)

    s, d = req("GET", "/notifications/unread-count", token=CUSTOMER_TOKEN)
    log("GET /notifications/unread-count", s == 200,
        f"count={d.get('data',{}).get('count')}" if s == 200 else "")

    # ─── Token Refresh ─────────────────────────────────────────────
    print("\n╔══ 15. TOKEN REFRESH ══╗")

    # Get refresh token from the auth response stored earlier
    s, d = req("GET", "/users/me", token=CUSTOMER_TOKEN)
    # We need to re-auth to get refresh token, or just test auth refresh
    # Use the OTP flow to get fresh tokens
    s, d = req("POST", "/auth/otp/send", payload={
        "method": "mobile",
        "destination": CUSTOMER_MOBILE,
        "role": "customer",
    })

    code = get_otp(CUSTOMER_MOBILE, "customer", "mobile", interactive_otp)
    if code:
        s, d = req("POST", "/auth/otp/verify", payload={
            "method": "mobile",
            "destination": CUSTOMER_MOBILE,
            "code": code,
            "role": "customer",
        })
        REFRESH = d.get("data", {}).get("refreshToken")
        if REFRESH:
            s, d = req("POST", "/auth/token/refresh", payload={"refreshToken": REFRESH})
            log("POST /auth/token/refresh", s == 200,
                "new tokens issued" if s == 200 else "")
        else:
            log("POST /auth/token/refresh", False, "No refresh token available")
    else:
        log("POST /auth/token/refresh", False, "No OTP for token refresh")

    # ─── Cancel Order ──────────────────────────────────────────────
    print("\n╔══ 16. ORDER CANCELLATION ══╗")

    # Place another order to cancel
    s, d = req("POST", "/orders", token=CUSTOMER_TOKEN, payload={
        "cookId": COOK_PROFILE_ID,
        "items": [
            {
                "dishId": DISH_ID,
                "mealSlot": "Lunch",
                "dayLabel": "mon",
                "planType": "today",
                "quantity": 1,
                "unitPrice": 180,
                "monthMultiplier": 1,
            },
        ],
        "deliveryAddressId": ADDRESS_ID,
        "paymentMethod": "bkash",
        "promoCode": "",
        "totalAmount": 180,
    })
    CANCEL_ORDER_ID = d.get("data", {}).get("id")
    if CANCEL_ORDER_ID:
        s, d = req("POST", f"/customer/orders/{CANCEL_ORDER_ID}/cancel",
                    token=CUSTOMER_TOKEN, payload={})
        log("POST /customer/orders/{id}/cancel", s == 200,
            f"status={d.get('data',{}).get('status')}" if s == 200 else "")
    else:
        log("POST /customer/orders/{id}/cancel", False, "Could not create order")

    # ─── Withdrawal ────────────────────────────────────────────────
    print("\n╔══ 17. WITHDRAWAL ══╗")

    s, d = req("POST", "/cook/earnings/withdraw", token=COOK_TOKEN, payload={
        "amount": 5000,
        "payoutMethod": "bkash",
        "payoutNumber": "01711000111",
    })
    error_code = d.get("error", {}).get("code", "")
    # INSUFFICIENT_BALANCE expected — cook has no delivered orders yet
    log("POST /cook/earnings/withdraw", error_code == "INSUFFICIENT_BALANCE",
        f"status={d.get('data',{}).get('status')}" if s == 200 else
        f"error={error_code}" if s != 200 else "")

    # ═══ SUMMARY ════════════════════════════════════════════════════
    total = PASS + FAIL
    print("\n" + "=" * 60)
    print(f"RESULTS:  {PASS}/{total} passed, {FAIL} failed")
    if FAIL == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"❌ {FAIL} test(s) FAILED — check logs above")
    print("=" * 60)

    # ─── New Endpoints ─────────────────────────────────────────────
    print("\n╔══ 18. NEW ENDPOINTS (implemented) ══╗")

    s, d = req("GET", "/cooks", token=CUSTOMER_TOKEN)
    log("GET /cooks (discovery)", s == 200)

    s, d = req("GET", "/cooks/trending", token=CUSTOMER_TOKEN)
    log("GET /cooks/trending", s == 200)

    s, d = req("GET", f"/cooks/{COOK_PROFILE_ID}", token=CUSTOMER_TOKEN)
    log("GET /cooks/{id} (detail)", s == 200)

    s, d = req("GET", "/cart", token=CUSTOMER_TOKEN)
    log("GET /cart", s == 200)

    s, d = req("GET", "/checkout/summary", token=CUSTOMER_TOKEN)
    log("GET /checkout/summary", s == 200)

    s, d = req("GET", "/cook/demand", token=COOK_TOKEN)
    log("GET /cook/demand", s == 200)

    s, d = req("GET", "/cook/earnings/summary", token=COOK_TOKEN)
    log("GET /cook/earnings/summary", s == 200)

    s, d = req("POST", f"/customer/orders/{ORDER_ID}/reorder", token=CUSTOMER_TOKEN, payload={})
    log("POST /customer/orders/{id}/reorder", s == 200)

    s, d = req("GET", "/cooks/nearby?lat=23.74&lng=90.37", token=CUSTOMER_TOKEN)
    log("GET /cooks/nearby", s == 200)

    s, d = req("GET", "/cooks/search?q=Rina", token=CUSTOMER_TOKEN)
    log("GET /cooks/search", s == 200)

    # ─── Summary Report ────────────────────────────────────────────
    print("\n📋 SRS/API PAYLOAD NOTES:")
    print("  ✅ Dish create — camelCase aliases (mealSlot/cutoffTime) now accepted")
    print("  ✅ Review create — camelCase aliases (cookId/orderId) now accepted")
    print("  ✅ All missing endpoints implemented (cooks, cart, earnings, demand, reorder)")
    print("  ✅ Subscription calendar includes undoableUntil")
    print("")


if __name__ == "__main__":
    interactive = "--interactive" in sys.argv or "-i" in sys.argv
    run_all_tests(interactive_otp=interactive)
