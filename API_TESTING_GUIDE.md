# KHABAR API Testing Guide

This guide covers manual testing with Postman and the automated test runner.

## Base URL

`http://127.0.0.1:8000/api/v1`

## Auth and Tokens

All protected endpoints require:

```
Authorization: Bearer <accessToken>
```

OTP flow endpoints:

- `POST /auth/otp/send`
- `POST /auth/otp/verify`
- `POST /auth/token/refresh`
- `POST /auth/logout`

### Send OTP

```
POST /auth/otp/send
{
	"method": "mobile",
	"destination": "+8801711000111",
	"role": "cook"
}
```

### Verify OTP

```
POST /auth/otp/verify
{
	"method": "mobile",
	"destination": "+8801711000111",
	"code": "123456",
	"role": "cook"
}
```

Response data includes `accessToken`, `refreshToken`, and `isNewUser`.

## Postman Environment Variables

Recommended variables:

- `BASE_URL` = `http://127.0.0.1:8000/api/v1`
- `COOK_TOKEN`
- `CUSTOMER_TOKEN`
- `COOK_ID`
- `DISH_ID`
- `ORDER_ID`
- `ADDRESS_ID`
- `SUBSCRIPTION_ID`

## Suggested Manual Test Flow

Follow this sequence to avoid dependency failures.

### 1) Cook auth

```
POST /auth/otp/send
POST /auth/otp/verify
```

Set `COOK_TOKEN` from `accessToken`.

### 2) Cook onboarding

```
PATCH /cook/onboarding/name
{
	"displayName": "Rina Begum"
}

PATCH /cook/onboarding/profile
{
	"bio": "Home cook specialising in Bangladeshi cuisine since 2015.",
	"avatarUrl": "https://cdn.khabar.app/avatars/usr_abc.jpg",
	"cuisineTypes": ["Bengali", "Mughal", "Street Food"]
}

PATCH /cook/onboarding/specialties
{
	"specialties": ["Biryani", "Kacchi", "Pulao"]
}

PATCH /cook/onboarding/service-area
{
	"areaLabel": "Dhanmondi",
	"radiusKm": 3,
	"coordinates": {"lat": 23.7461, "lng": 90.3742}
}

POST /cook/onboarding/identity
{}

PATCH /cook/onboarding/payout
{
	"payoutMethod": "bkash",
	"payoutNumber": "01711000111",
	"payoutAccountName": "Rina Begum"
}

POST /cook/onboarding/complete
{}

GET /cook/onboarding/status
```

### 3) Cook profile

```
GET /cook/profile
PATCH /cook/profile
{
	"bio": "Updated bio"
}

PATCH /cook/profile/holiday-mode
{
	"enabled": true
}
```

Store `COOK_ID` from `GET /cook/profile`.

### 4) Menu

```
POST /cook/menu/dishes
{
	"name": "Kacchi Biryani",
	"description": "Aromatic kacchi with potato and egg.",
	"category": "Biryani",
	"meal_slot": "Lunch",
	"days": ["mon", "wed", "fri"],
	"price": 180,
	"capacity": 10,
	"cutoff_time": "10:00",
	"image_url": "https://cdn.khabar.app/dishes/kacchi.jpg",
	"add_ons_label": "Extra egg +20"
}

GET /cook/menu
GET /cooks/{COOK_ID}/menu

PATCH /cook/menu/dishes/{DISH_ID}/availability
{
	"available": false
}
```

CamelCase write aliases are accepted for dish create:

- `mealSlot` for `meal_slot`
- `cutoffTime` for `cutoff_time`
- `imageUrl` for `image_url`
- `addOnsLabel` for `add_ons_label`

### 5) Customer auth

```
POST /auth/otp/send
POST /auth/otp/verify
```

Set `CUSTOMER_TOKEN`.

### 6) Customer onboarding

```
PATCH /customer/onboarding/profile
{
	"displayName": "Ayesha Rahman",
	"avatarUrl": null
}

POST /customer/onboarding/complete
{}
```

### 7) Addresses

```
POST /customer/addresses
{
	"label": "Home",
	"line1": "House 12, Road 4, Dhanmondi, Dhaka-1209",
	"line2": null,
	"coordinates": {"lat": 23.7461, "lng": 90.3742},
	"is_default": true
}

GET /customer/addresses
```

Store `ADDRESS_ID`.

### 8) Orders and payment

```
POST /orders
{
	"cookId": "{COOK_ID}",
	"items": [
		{
			"dishId": "{DISH_ID}",
			"mealSlot": "Lunch",
			"dayLabel": "mon",
			"planType": "monthly",
			"quantity": 2,
			"unitPrice": 180,
			"monthMultiplier": 4
		}
	],
	"deliveryAddressId": "{ADDRESS_ID}",
	"paymentMethod": "bkash",
	"promoCode": "",
	"totalAmount": 1440
}

POST /webhooks/payment
{
	"orderId": "{ORDER_ID}",
	"status": "success",
	"transactionId": "txn_test_001"
}
```

### 9) Customer orders

```
GET /customer/orders
GET /customer/orders/{ORDER_ID}
POST /customer/orders/{ORDER_ID}/cancel
POST /customer/orders/{ORDER_ID}/reorder
```

### 10) Subscriptions

```
GET /customer/subscriptions
GET /customer/subscriptions/{SUBSCRIPTION_ID}
GET /customer/subscriptions/{SUBSCRIPTION_ID}/calendar?month=2026-05
POST /customer/subscriptions/{SUBSCRIPTION_ID}/pause
POST /customer/subscriptions/{SUBSCRIPTION_ID}/resume
POST /customer/subscriptions/{SUBSCRIPTION_ID}/cancel
POST /customer/subscriptions/{SUBSCRIPTION_ID}/deliveries/{DELIVERY_ID}/skip
POST /customer/subscriptions/{SUBSCRIPTION_ID}/deliveries/{DELIVERY_ID}/resume
```

Calendar response includes `undoableUntil`.

### 11) Reviews

```
POST /customer/reviews
{
	"cook": "{COOK_ID}",
	"order": "{ORDER_ID}",
	"rating": 4.5,
	"comment": "Excellent biryani, delivered on time!"
}

GET /customer/reviews
GET /cooks/{COOK_ID}/reviews
```

CamelCase write aliases are accepted:

- `cookId` for `cook`
- `orderId` for `order`

### 12) Notifications

```
GET /notifications
GET /notifications/unread-count
PATCH /notifications/{NOTIFICATION_ID}/read
PATCH /notifications/read-all
```

### 13) Cook earnings

```
GET /cook/earnings/summary
GET /cook/earnings/trend
GET /cook/earnings/transactions
POST /cook/earnings/withdraw
```

### 14) Demand and cart

```
GET /cook/demand
POST /cook/demand/{DEMAND_ID}/lock
PATCH /cook/demand/{DEMAND_ID}/status

GET /cart
POST /cart/items
PATCH /cart/items/{ITEM_ID}
DELETE /cart/items/{ITEM_ID}
POST /cart/promo
DELETE /cart/promo
DELETE /cart
GET /checkout/summary
```

### 15) Discovery

```
GET /cooks
GET /cooks/nearby?lat=23.74&lng=90.37
GET /cooks/trending
GET /cooks/search?q=Rina
GET /cooks/{COOK_ID}
```

## Full Automated Test Suite

Run from project root:

```
./.venv/bin/python test_api_full.py
```

Use `-i` or `--interactive` to enter OTP codes manually. Default mode reads OTP from DB.

## Endpoint Reference (Quick List)

Auth:

- `POST /auth/otp/send`
- `POST /auth/otp/verify`
- `POST /auth/token/refresh`
- `POST /auth/logout`

Users:

- `GET /users/me`
- `PATCH /users/me`

Cook onboarding:

- `PATCH /cook/onboarding/name`
- `PATCH /cook/onboarding/profile`
- `PATCH /cook/onboarding/specialties`
- `PATCH /cook/onboarding/service-area`
- `POST /cook/onboarding/identity`
- `PATCH /cook/onboarding/payout`
- `POST /cook/onboarding/complete`
- `GET /cook/onboarding/status`

Cook profile:

- `GET /cook/profile`
- `PATCH /cook/profile`
- `PATCH /cook/profile/holiday-mode`

Menu:

- `GET /cook/menu`
- `POST /cook/menu/dishes`
- `PATCH /cook/menu/dishes/{DISH_ID}`
- `DELETE /cook/menu/dishes/{DISH_ID}`
- `PATCH /cook/menu/dishes/{DISH_ID}/availability`
- `GET /cooks/{COOK_ID}/menu`

Orders and cart:

- `POST /orders`
- `GET /customer/orders`
- `GET /customer/orders/{ORDER_ID}`
- `POST /customer/orders/{ORDER_ID}/cancel`
- `POST /customer/orders/{ORDER_ID}/reorder`
- `GET /cart`
- `DELETE /cart`
- `POST /cart/items`
- `PATCH /cart/items/{ITEM_ID}`
- `DELETE /cart/items/{ITEM_ID}`
- `POST /cart/promo`
- `DELETE /cart/promo`
- `GET /checkout/summary`

Subscriptions:

- `GET /customer/subscriptions`
- `GET /customer/subscriptions/{SUBSCRIPTION_ID}`
- `GET /customer/subscriptions/{SUBSCRIPTION_ID}/calendar`
- `POST /customer/subscriptions/{SUBSCRIPTION_ID}/pause`
- `POST /customer/subscriptions/{SUBSCRIPTION_ID}/resume`
- `POST /customer/subscriptions/{SUBSCRIPTION_ID}/cancel`
- `POST /customer/subscriptions/{SUBSCRIPTION_ID}/deliveries/{DELIVERY_ID}/skip`
- `POST /customer/subscriptions/{SUBSCRIPTION_ID}/deliveries/{DELIVERY_ID}/resume`

Payments:

- `GET /cook/earnings/summary`
- `GET /cook/earnings/trend`
- `GET /cook/earnings/transactions`
- `POST /cook/earnings/withdraw`
- `GET /cook/earnings/withdrawals`
- `POST /webhooks/payment`

Reviews:

- `POST /customer/reviews`
- `GET /customer/reviews`
- `GET /cooks/{COOK_ID}/reviews`

Notifications:

- `GET /notifications`
- `PATCH /notifications/{NOTIFICATION_ID}/read`
- `PATCH /notifications/read-all`
- `GET /notifications/unread-count`

Locations:

- `GET /customer/addresses`
- `POST /customer/addresses`
- `PATCH /customer/addresses/{ADDRESS_ID}`
- `DELETE /customer/addresses/{ADDRESS_ID}`
- `PATCH /customer/addresses/{ADDRESS_ID}/default`

Customers:

- `PATCH /customer/onboarding/profile`
- `POST /customer/onboarding/complete`

Discovery:

- `GET /cooks`
- `GET /cooks/nearby`
- `GET /cooks/trending`
- `GET /cooks/search`
- `GET /cooks/{COOK_ID}`

Demand:

- `GET /cook/demand`
- `POST /cook/demand/{DEMAND_ID}/lock`
- `PATCH /cook/demand/{DEMAND_ID}/status`
