# Khabar — Software Requirements Specification (SRS)
**Version:** 1.0  
**Date:** May 2026  
**Audience:** Backend Engineers, API Designers, QA Engineers

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [User Roles & Personas](#2-user-roles--personas)
3. [Authentication Module](#3-authentication-module)
4. [Cook Onboarding Module](#4-cook-onboarding-module)
5. [Customer Onboarding Module](#5-customer-onboarding-module)
6. [Cook — Menu Management](#6-cook--menu-management)
7. [Cook — Orders & Production](#7-cook--orders--production)
8. [Cook — Earnings & Payouts](#8-cook--earnings--payouts)
9. [Cook — Profile & Settings](#9-cook--profile--settings)
10. [Customer — Discovery & Search](#10-customer--discovery--search)
11. [Customer — Cook Detail & Menu](#11-customer--cook-detail--menu)
12. [Customer — Cart & Checkout](#12-customer--cart--checkout)
13. [Customer — Orders](#13-customer--orders)
14. [Customer — Subscriptions](#14-customer--subscriptions)
15. [Customer — Profile & Settings](#15-customer--profile--settings)
16. [Notifications](#16-notifications)
17. [Data Models (Full Schema)](#17-data-models-full-schema)
18. [API Endpoint Reference](#18-api-endpoint-reference)
19. [State Machine Definitions](#19-state-machine-definitions)
20. [Error Codes & Responses](#20-error-codes--responses)

---

## 1. System Overview

**Khabar** is a home-cook marketplace operating in Bangladesh. It connects verified home cooks with customers who want daily/monthly home-cooked meals delivered to their address.

### Core Value Propositions
- Customers subscribe to a cook's weekly menu for recurring daily deliveries
- Customers can also place one-off orders for single days
- Cooks manage a weekly menu, set capacity per dish, and track a production pipeline
- Platform takes a service fee; cooks withdraw earnings via bKash/Nagad

### Tech Stack Context
- **Mobile App:** React Native + Expo (TypeScript)
- **Auth:** OTP-based (SMS/Email), 6-digit code
- **Currency:** Bangladeshi Taka (BDT / Tk)
- **Region:** Bangladesh (+880 dialing code)

---

## 2. User Roles & Personas

| Role | Description |
|------|-------------|
| `customer` | End user who browses cooks, orders meals, manages subscriptions |
| `cook` | Home cook who lists a weekly menu, manages production, receives payouts |
| `admin` | Platform operator (out of scope for v1 API, referenced for completeness) |

---

## 3. Authentication Module

### 3.1 Overview
OTP-based, passwordless authentication. Both roles share the same auth flow with a `role` discriminator.

### 3.2 Flows

#### 3.2.1 Sign Up
```
User selects role (customer | cook)
  → Enters mobile (+880 XXXXXXXXXX) OR email
  → POST /auth/otp/send  { method, destination, role }
  → Enters 6-digit OTP
  → POST /auth/otp/verify  { method, destination, code, role }
  ← Returns: { accessToken, refreshToken, user, isNewUser: true }
  → If isNewUser=true → redirect to onboarding flow
```

#### 3.2.2 Sign In (returning user)
```
  → POST /auth/otp/send  { method, destination, role }
  → POST /auth/otp/verify  { method, destination, code, role }
  ← Returns: { accessToken, refreshToken, user, isNewUser: false }
  → If isNewUser=false → redirect to dashboard
```

#### 3.2.3 Token Refresh
```
  → POST /auth/token/refresh  { refreshToken }
  ← Returns: { accessToken, refreshToken }
```

#### 3.2.4 Sign Out
```
  → POST /auth/logout  { refreshToken }
  ← 204 No Content
```

### 3.3 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/otp/send` | None | Send OTP to mobile or email |
| POST | `/auth/otp/verify` | None | Verify OTP, return tokens |
| POST | `/auth/token/refresh` | None | Refresh access token |
| POST | `/auth/logout` | Bearer | Invalidate refresh token |

### 3.4 Request / Response Schemas

**POST /auth/otp/send**
```json
// Request
{
  "method": "mobile" | "email",
  "destination": "+8801711000111" | "user@example.com",
  "role": "customer" | "cook"
}

// Response 200
{
  "message": "OTP sent",
  "expiresInSeconds": 120,
  "cooldownSeconds": 22
}
```

**POST /auth/otp/verify**
```json
// Request
{
  "method": "mobile" | "email",
  "destination": "+8801711000111",
  "code": "123456",
  "role": "customer" | "cook"
}

// Response 200
{
  "accessToken": "eyJ...",
  "refreshToken": "eyJ...",
  "isNewUser": true,
  "user": {
    "id": "usr_abc123",
    "role": "cook",
    "displayName": null,
    "avatarUrl": null,
    "mobile": "+8801711000111",
    "email": null,
    "verificationStatus": "unverified",
    "onboardingStep": "name",
    "createdAt": "2026-04-18T10:00:00Z"
  }
}
```

---

## 4. Cook Onboarding Module

### 4.1 Onboarding Steps (in order)

| Step Key | Screen | Data Collected |
|----------|--------|----------------|
| `name` | CookNameScreen | `displayName` |
| `profile` | CookProfileDetailsScreen | `bio`, `avatarUrl`, `cuisineTypes[]` |
| `specialties` | CookSpecialtiesScreen | `specialties[]` (tags) |
| `serviceArea` | CookServiceAreaScreen | `areaLabel`, `radiusKm`, `coordinates` |
| `identity` | CookIdentityVerificationScreen | `nidFront`, `nidBack`, `selfie` |
| `payout` | CookPayoutScreen | `payoutMethod`, `payoutNumber`, `payoutAccountName` |
| `complete` | CookCompleteScreen | — (marks onboarding done) |

### 4.2 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| PATCH | `/cook/onboarding/name` | Bearer | Save display name |
| PATCH | `/cook/onboarding/profile` | Bearer | Save bio, avatar, cuisines |
| PATCH | `/cook/onboarding/specialties` | Bearer | Save specialty tags |
| PATCH | `/cook/onboarding/service-area` | Bearer | Save delivery area |
| POST | `/cook/onboarding/identity` | Bearer | Upload NID + selfie (multipart) |
| PATCH | `/cook/onboarding/payout` | Bearer | Save payout account |
| POST | `/cook/onboarding/complete` | Bearer | Mark onboarding complete |
| GET | `/cook/onboarding/status` | Bearer | Get current onboarding step |

### 4.3 Request Schemas

**PATCH /cook/onboarding/profile**
```json
{
  "bio": "Home cook specialising in Bangladeshi cuisine since 2015.",
  "avatarUrl": "https://cdn.khabar.app/avatars/usr_abc.jpg",
  "cuisineTypes": ["Bengali", "Mughal", "Street Food"]
}
```

**PATCH /cook/onboarding/service-area**
```json
{
  "areaLabel": "Dhanmondi",
  "radiusKm": 3,
  "coordinates": { "lat": 23.7461, "lng": 90.3742 }
}
```

**POST /cook/onboarding/identity** — `multipart/form-data`
```
nidFront: <file>
nidBack: <file>
selfie: <file>
```

**PATCH /cook/onboarding/payout**
```json
{
  "payoutMethod": "bkash" | "nagad" | "bank",
  "payoutNumber": "01711000111",
  "payoutAccountName": "Rina Begum"
}
```

### 4.4 Cook Verification Status State Machine
```
unverified → pending_review → approved
                           → rejected → pending_review (re-submit)
```

---

## 5. Customer Onboarding Module

### 5.1 Steps

| Step | Screen | Data Collected |
|------|--------|----------------|
| `profile` | CustomerProfileScreen (mode=onboarding) | `displayName`, `avatarUrl` |

Customer onboarding is minimal — just a display name and optional avatar.

### 5.2 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| PATCH | `/customer/onboarding/profile` | Bearer | Save name + avatar |
| POST | `/customer/onboarding/complete` | Bearer | Mark onboarding done |

---

## 6. Cook — Menu Management

### 6.1 Overview
Cooks define a **weekly recurring menu**. Each entry is a `Dish` assigned to a `DayKey` + `MealSlot`. Dishes are available/unavailable and have a daily capacity and cutoff time.

### 6.2 Data Concepts

- **DayKey:** `mon | tue | wed | thu | fri | sat | sun`
- **MealSlot:** `Breakfast | Lunch | Dinner`
- **CutoffTime:** Time before which orders must be placed (e.g. `10:00`)
- **Capacity:** Max number of portions a cook can fulfill per day per dish

### 6.3 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/cook/menu` | Bearer | Get full weekly menu |
| POST | `/cook/menu/dishes` | Bearer | Create a new dish |
| PATCH | `/cook/menu/dishes/:dishId` | Bearer | Update dish details |
| DELETE | `/cook/menu/dishes/:dishId` | Bearer | Delete dish |
| PATCH | `/cook/menu/dishes/:dishId/availability` | Bearer | Toggle available/unavailable |
| GET | `/cook/menu/dishes/:dishId` | Bearer | Get single dish |

### 6.4 Request / Response Schemas

**POST /cook/menu/dishes**
```json
// Request
{
  "name": "Kacchi Biryani",
  "description": "Aromatic kacchi with potato and egg.",
  "category": "Biryani",
  "mealSlot": "Lunch",
  "days": ["mon", "wed", "fri"],
  "price": 180,
  "capacity": 10,
  "cutoffTime": "10:00",
  "imageUrl": "https://cdn.khabar.app/dishes/kacchi.jpg",
  "addOnsLabel": "Extra egg +20"
}

// Response 201
{
  "id": "dish_abc123",
  "cookId": "usr_cook1",
  "name": "Kacchi Biryani",
  "description": "...",
  "category": "Biryani",
  "mealSlot": "Lunch",
  "days": ["mon", "wed", "fri"],
  "price": 180,
  "capacity": 10,
  "cutoffTime": "10:00",
  "imageUrl": "...",
  "available": true,
  "createdAt": "2026-04-18T10:00:00Z"
}
```

**GET /cook/menu**
```json
{
  "cookId": "usr_cook1",
  "menu": {
    "mon": [
      {
        "id": "dish_abc123",
        "name": "Kacchi Biryani",
        "mealSlot": "Lunch",
        "price": 180,
        "capacity": 10,
        "cutoffTime": "10:00",
        "available": true,
        "imageUrl": "...",
        "category": "Biryani",
        "description": "..."
      }
    ],
    "tue": [],
    "wed": [...],
    ...
  }
}
```

---

## 7. Cook — Orders & Production

### 7.1 Overview
Each day, the cook sees a **Demand Board** — a list of `DemandItem` objects, one per dish per meal slot. Each `DemandItem` aggregates all orders into a single production unit.

### 7.2 DemandItem Composition

```
DemandItem
├── dishId / dishName / mealSlot
├── cutoffLabel
├── baseline      ← total from active subscriptions
├── oneOff        ← total from one-off orders for today
├── overrides     ← quantity additions from overrides
├── cancellations ← quantity removals
├── capacity      ← cook's max for this dish today
├── isLocked      ← plan locked, no more changes accepted
├── productionStatus
└── contributions[] ← per-customer breakdown
```

**Total = baseline + oneOff + overrides - cancellations**

### 7.3 Production Status State Machine

```
pending → preparing → packed → outForDelivery → delivered
```

| Status | Meaning |
|--------|---------|
| `pending` | Demand aggregated, cook hasn't started |
| `preparing` | Cook is actively cooking |
| `packed` | Meals are packed and ready |
| `outForDelivery` | On the way to customers |
| `delivered` | All deliveries completed |

### 7.4 Plan Lock
Before a cutoff time passes, the cook can **lock the plan**. Once locked:
- No new orders accepted for this dish/day
- Production status can begin advancing

### 7.5 Contribution Types

| Type | Source |
|------|--------|
| `Subscription` | Customer's active recurring subscription |
| `One-off` | Customer's single-day order |
| `Override` | Customer increased their quantity for today |
| `Cancellation` | Customer cancelled/reduced for today |

### 7.6 Per-Customer Delivery Tracking
Each `DemandContribution` has `isDelivered: boolean`. Cook marks individual customers delivered from the delivery list.

### 7.7 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/cook/demand` | Bearer | Get today's demand board |
| GET | `/cook/demand?date=YYYY-MM-DD` | Bearer | Get demand for specific date |
| POST | `/cook/demand/:demandItemId/lock` | Bearer | Lock production plan |
| PATCH | `/cook/demand/:demandItemId/status` | Bearer | Advance production status |
| PATCH | `/cook/demand/:demandItemId/contributions/:contributionId/delivered` | Bearer | Mark single customer delivered |
| GET | `/cook/demand/:demandItemId/contributions` | Bearer | List all customer contributions |

### 7.8 Request / Response Schemas

**GET /cook/demand**
```json
{
  "date": "2026-04-18",
  "dayLabel": "Friday",
  "demandItems": [
    {
      "id": "demand_abc",
      "dishId": "dish_abc123",
      "dishName": "Rice + Chicken Curry",
      "mealSlot": "Lunch",
      "cutoffLabel": "Cutoff 10:00 AM",
      "cutoffTime": "10:00",
      "baseline": 5,
      "oneOff": 2,
      "overrides": 1,
      "cancellations": 0,
      "capacity": 8,
      "isLocked": false,
      "productionStatus": "pending",
      "contributions": [
        {
          "id": "contrib_1",
          "customerId": "usr_cust1",
          "customerName": "Ayesha Rahman",
          "companyName": "ByteBridge Ltd",
          "deliveryAddress": "House 12, Road 4, Dhanmondi",
          "phoneNumber": "01711000111",
          "quantity": 3,
          "type": "Subscription",
          "isDelivered": false
        }
      ]
    }
  ]
}
```

**PATCH /cook/demand/:demandItemId/status**
```json
// Request
{ "status": "preparing" | "packed" | "outForDelivery" | "delivered" }

// Response 200
{ "id": "demand_abc", "productionStatus": "preparing", "updatedAt": "..." }
```

**PATCH /cook/demand/:id/contributions/:cid/delivered**
```json
// Request
{ "isDelivered": true }

// Response 200
{ "contributionId": "contrib_1", "isDelivered": true, "deliveredAt": "..." }
```

---

## 8. Cook — Earnings & Payouts

### 8.1 Overview
Cook sees total earnings, available balance, weekly/monthly trend, and can withdraw.

### 8.2 Earnings Composition

```
grossEarnings = sum of all delivered order values
platformFee  = grossEarnings × feeRate (e.g. 10%)
netEarnings  = grossEarnings - platformFee
availableBalance = netEarnings - totalWithdrawn
```

### 8.3 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/cook/earnings/summary` | Bearer | Balance + stats summary |
| GET | `/cook/earnings/trend?range=week\|month` | Bearer | Trend data points |
| GET | `/cook/earnings/transactions` | Bearer | Paginated transaction list |
| POST | `/cook/earnings/withdraw` | Bearer | Initiate withdrawal |
| GET | `/cook/earnings/withdrawals` | Bearer | Withdrawal history |

### 8.4 Schemas

**GET /cook/earnings/summary**
```json
{
  "availableBalance": 12450,
  "totalEarnings": 48000,
  "thisMonthEarnings": 8200,
  "platformFeeRate": 0.10,
  "pendingWithdrawal": 0
}
```

**GET /cook/earnings/trend?range=week**
```json
{
  "range": "week",
  "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
  "values": [1200, 1800, 1500, 2100, 1900, 2400, 1600]
}
```

**POST /cook/earnings/withdraw**
```json
// Request
{
  "amount": 5000,
  "payoutMethod": "bkash",
  "payoutNumber": "01711000111"
}

// Response 202
{
  "withdrawalId": "wdl_xyz",
  "amount": 5000,
  "status": "processing",
  "estimatedCompletionMinutes": 30
}
```

### 8.5 Withdrawal Status State Machine
```
processing → completed
           → failed → (retry possible)
```

---

## 9. Cook — Profile & Settings

### 9.1 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/cook/profile` | Bearer | Get full cook profile |
| PATCH | `/cook/profile` | Bearer | Update name, bio, avatar |
| PATCH | `/cook/profile/holiday-mode` | Bearer | Toggle holiday mode on/off |
| GET | `/cook/profile/stats` | Bearer | Orders, reviews, rating, monthly earnings |
| PATCH | `/cook/service-area` | Bearer | Update service area |
| GET | `/cook/verification` | Bearer | Get verification status + docs |
| PATCH | `/cook/payout` | Bearer | Update payout info |
| GET | `/cook/notifications/settings` | Bearer | Get notification preferences |
| PATCH | `/cook/notifications/settings` | Bearer | Update notification preferences |

### 9.2 Holiday Mode

When `holidayModeEnabled = true`:
- Cook does not appear in search results
- All upcoming subscription deliveries are paused
- No new orders can be placed with this cook

**PATCH /cook/profile/holiday-mode**
```json
// Request
{ "enabled": true }

// Response 200
{ "holidayModeEnabled": true, "pausedUntil": null }
```

---

## 10. Customer — Discovery & Search

### 10.1 Overview
Customer browses a feed of nearby cooks on the dashboard. Filters by category, quick filters (verified, fast delivery, home kitchen). Full-text search by cook name, dish name, cuisine.

### 10.2 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/cooks` | Bearer | Paginated cook list with filters |
| GET | `/cooks/trending` | Bearer | Trending cooks (featured feed) |
| GET | `/cooks/nearby` | Bearer | Cooks sorted by proximity |
| GET | `/cooks/search?q=` | Bearer | Full-text search |
| GET | `/categories` | Bearer | Cuisine category list |

### 10.3 Query Parameters for GET /cooks

| Param | Type | Description |
|-------|------|-------------|
| `lat` | float | Customer latitude |
| `lng` | float | Customer longitude |
| `radiusKm` | int | Search radius (default 5) |
| `category` | string | Cuisine category filter |
| `verified` | bool | Only verified cooks |
| `mealSlot` | string | `Breakfast\|Lunch\|Dinner` |
| `page` | int | Pagination page |
| `limit` | int | Results per page (default 20) |

### 10.4 Response Schema

**GET /cooks/nearby**
```json
{
  "page": 1,
  "totalCount": 42,
  "cooks": [
    {
      "id": "usr_cook1",
      "displayName": "Rina Begum",
      "avatarUrl": "...",
      "areaLabel": "Dhanmondi",
      "distanceKm": 1.2,
      "etaLabel": "30-40 min",
      "rating": 4.8,
      "reviewCount": 234,
      "cuisines": ["Bengali", "Mughal"],
      "priceLabel": "Tk 120–200",
      "isVerified": true,
      "holidayModeEnabled": false,
      "featuredImageUrl": "..."
    }
  ]
}
```

---

## 11. Customer — Cook Detail & Menu

### 11.1 Overview
Customer views a cook's profile, weekly menu grouped by day and meal slot, and can add items to cart.

### 11.2 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/cooks/:cookId` | Bearer | Cook profile + stats |
| GET | `/cooks/:cookId/menu` | Bearer | Full weekly menu |
| GET | `/cooks/:cookId/menu?day=mon&slot=Lunch` | Bearer | Filtered menu |
| GET | `/cooks/:cookId/reviews` | Bearer | Paginated reviews |

### 11.3 Menu Response Schema

**GET /cooks/:cookId/menu**
```json
{
  "cookId": "usr_cook1",
  "cookName": "Rina Begum",
  "menu": {
    "mon": [
      {
        "id": "dish_abc123",
        "name": "Kacchi Biryani",
        "description": "Aromatic kacchi with potato and egg.",
        "category": "Biryani",
        "mealSlot": "Lunch",
        "price": 180,
        "cutoffTime": "10:00",
        "cutoffLabel": "Cutoff 10 AM",
        "available": true,
        "capacity": 10,
        "remainingCapacity": 6,
        "imageUrl": "...",
        "addOnsLabel": "Extra egg +20",
        "isPopular": true
      }
    ]
  }
}
```

---

## 12. Customer — Cart & Checkout

### 12.1 Plan Types

| Type | Description |
|------|-------------|
| `monthly` | Recurring subscription — ordered for all matching weekdays in the month |
| `today` | One-off single-day order |

### 12.2 Month Multiplier
For `monthly` plan items, `monthMultiplier` = number of matching weekdays in the billing month (e.g. 4 Mondays = 4).

**lineTotal = unitPrice × quantity × monthMultiplier**

### 12.3 Promo Codes

| Code | Type | Value |
|------|------|-------|
| `MONTHLY10` | percent | 10% off |
| `MEAL100` | fixed | Tk 100 off |
| `KHABAR20` | percent | 20% off |

### 12.4 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/cart` | Bearer | Get current cart |
| POST | `/cart/items` | Bearer | Add item to cart |
| PATCH | `/cart/items/:rowId` | Bearer | Update quantity |
| DELETE | `/cart/items/:rowId` | Bearer | Remove item |
| DELETE | `/cart` | Bearer | Clear cart |
| POST | `/cart/promo` | Bearer | Apply promo code |
| DELETE | `/cart/promo` | Bearer | Remove promo code |
| GET | `/checkout/summary` | Bearer | Price breakdown for cart |
| POST | `/orders` | Bearer | Place order (checkout confirm) |

### 12.5 Cart Item Schema

```json
{
  "rowId": "dish_abc::monthly::Monday::Lunch::4",
  "cookId": "usr_cook1",
  "cookName": "Rina Begum",
  "dishKey": "dish_abc123",
  "dishName": "Kacchi Biryani",
  "mealSlot": "Lunch",
  "dayLabel": "Monday",
  "imageUrl": "...",
  "unitPrice": 180,
  "quantity": 2,
  "monthMultiplier": 4,
  "planType": "monthly" | "today"
}
```

### 12.6 Checkout Summary Schema

```json
{
  "items": [...],
  "subtotal": 1440,
  "promoCode": "MONTHLY10",
  "promoDiscount": 144,
  "deliveryFee": 0,
  "platformFee": 0,
  "total": 1296,
  "currency": "BDT"
}
```

### 12.7 POST /orders — Place Order

```json
// Request
{
  "cookId": "usr_cook1",
  "items": [
    {
      "dishId": "dish_abc123",
      "mealSlot": "Lunch",
      "dayLabel": "Monday",
      "planType": "monthly",
      "quantity": 2,
      "unitPrice": 180,
      "monthMultiplier": 4
    }
  ],
  "deliveryAddressId": "addr_home1",
  "paymentMethod": "bkash" | "nagad" | "card",
  "promoCode": "MONTHLY10",
  "totalAmount": 1296
}

// Response 201
{
  "orderId": "ord_xyz789",
  "status": "confirmed",
  "planType": "monthly",
  "startDate": "2026-05-01",
  "endDate": "2026-05-31",
  "totalAmount": 1296,
  "paymentStatus": "pending",
  "paymentRedirectUrl": "https://payment.bkash.com/...",
  "createdAt": "2026-04-18T12:00:00Z"
}
```

### 12.8 Payment Flow

```
POST /orders → { paymentRedirectUrl }
  → Customer completes payment on bKash/Nagad
  → Webhook: POST /webhooks/payment { orderId, status, transactionId }
  → Order status updated to confirmed/failed
```

### 12.9 Address Management

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/customer/addresses` | Bearer | List saved addresses |
| POST | `/customer/addresses` | Bearer | Add new address |
| PATCH | `/customer/addresses/:id` | Bearer | Update address |
| DELETE | `/customer/addresses/:id` | Bearer | Delete address |
| PATCH | `/customer/addresses/:id/default` | Bearer | Set as default |

**Address Schema**
```json
{
  "id": "addr_home1",
  "label": "Home",
  "line1": "House 12, Road 4, Dhanmondi, Dhaka-1209",
  "line2": null,
  "coordinates": { "lat": 23.7461, "lng": 90.3742 },
  "isDefault": true
}
```

---

## 13. Customer — Orders

### 13.1 Order Status State Machine

```
confirmed → preparing → packed → outForDelivery → delivered
confirmed → cancelled
```

| Status | Trigger |
|--------|---------|
| `confirmed` | Payment successful |
| `preparing` | Cook advances production status |
| `packed` | Cook advances production status |
| `outForDelivery` | Cook advances production status |
| `delivered` | Cook marks all contributions delivered |
| `cancelled` | Customer cancels (before cutoff) OR payment fails |

### 13.2 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/customer/orders` | Bearer | Paginated order list |
| GET | `/customer/orders?status=active\|delivered\|cancelled` | Bearer | Filtered list |
| GET | `/customer/orders/:orderId` | Bearer | Single order detail |
| POST | `/customer/orders/:orderId/cancel` | Bearer | Cancel an order |
| POST | `/customer/orders/:orderId/reorder` | Bearer | Clone order into cart |

### 13.3 Order List Item Schema

```json
{
  "id": "ord_xyz789",
  "cookId": "usr_cook1",
  "cookName": "Rina Begum",
  "cookAvatarUrl": "...",
  "dishes": [
    { "name": "Rice + Chicken Curry", "quantity": 2 }
  ],
  "totalAmount": 1296,
  "status": "active" | "delivered" | "cancelled",
  "planType": "monthly" | "today",
  "deliveryAddress": "House 12, Road 4, Dhanmondi",
  "placedAt": "2026-04-18T12:00:00Z",
  "estimatedDeliveryTime": "2026-04-18T13:00:00Z"
}
```

---

## 14. Customer — Subscriptions

### 14.1 Overview
A `Subscription` is created when a customer places a `monthly` plan order. It generates daily delivery instances for each matching weekday in the billing period.

### 14.2 Subscription State Machine

```
active → paused → active (resume)
active → cancelled
```

### 14.3 Daily Delivery Instance State Machine

```
scheduled → delivered
scheduled → skipped (customer-initiated)
scheduled → skipped_paused (subscription paused)
delivered → scheduled (not applicable — terminal)
```

### 14.4 Pause Durations

| Key | Duration |
|-----|----------|
| `1w` | 7 days |
| `2w` | 14 days |
| `1m` | 30 days |
| `manual` | Until explicit resume |

### 14.5 Partial Quantity Pause/Skip
A customer with multiple portions (e.g. 3) can pause or skip a **subset** of portions. The remaining portions continue as normal.

### 14.6 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/customer/subscriptions` | Bearer | List all subscriptions |
| GET | `/customer/subscriptions/:subId` | Bearer | Subscription detail |
| GET | `/customer/subscriptions/:subId/calendar?month=2026-04` | Bearer | Monthly delivery calendar |
| POST | `/customer/subscriptions/:subId/pause` | Bearer | Pause subscription |
| POST | `/customer/subscriptions/:subId/resume` | Bearer | Resume paused subscription |
| POST | `/customer/subscriptions/:subId/cancel` | Bearer | Cancel subscription |
| POST | `/customer/subscriptions/:subId/deliveries/:deliveryId/skip` | Bearer | Skip single delivery day |
| POST | `/customer/subscriptions/:subId/deliveries/:deliveryId/resume` | Bearer | Undo a skip |

### 14.7 Schemas

**GET /customer/subscriptions/:subId**
```json
{
  "id": "sub_abc",
  "cookId": "usr_cook1",
  "cookName": "Rina Begum",
  "planName": "Weekday Lunch",
  "dishName": "Weekday Lunch",
  "mealSlot": "Lunch",
  "portionsPerDay": 3,
  "unitPrice": 120,
  "monthlyTotal": 2400,
  "monthlySavings": 200,
  "status": "active" | "paused" | "cancelled",
  "pausedUntil": null,
  "startDate": "2026-04-01",
  "endDate": "2026-04-30",
  "paymentMethod": "bkash",
  "stats": {
    "delivered": 17,
    "skipped": 2,
    "remaining": 10
  }
}
```

**GET /customer/subscriptions/:subId/calendar?month=2026-04**
```json
{
  "month": "2026-04",
  "deliveries": [
    {
      "id": "del_001",
      "date": "2026-04-01",
      "status": "delivered",
      "quantityDelivered": 3,
      "quantityOrdered": 3
    },
    {
      "id": "del_018",
      "date": "2026-04-18",
      "status": "scheduled",
      "isToday": true,
      "quantityOrdered": 3
    },
    {
      "id": "del_019",
      "date": "2026-04-19",
      "status": "skipped",
      "quantitySkipped": 2,
      "quantityOrdered": 3
    }
  ]
}
```

**POST /customer/subscriptions/:subId/pause**
```json
// Request
{
  "duration": "1w" | "2w" | "1m" | "manual",
  "quantity": 2
}

// Response 200
{
  "subscriptionId": "sub_abc",
  "status": "paused",
  "pausedPortions": 2,
  "totalPortions": 3,
  "pausedUntil": "2026-04-25T00:00:00Z",
  "remainingActivePortions": 1
}
```

**POST /customer/subscriptions/:subId/deliveries/:deliveryId/skip**
```json
// Request
{ "quantity": 2 }

// Response 200
{
  "deliveryId": "del_020",
  "date": "2026-04-20",
  "status": "skipped",
  "quantitySkipped": 2,
  "quantityRemaining": 1,
  "undoableUntil": "2026-04-20T09:00:00Z"
}
```

---

## 15. Customer — Profile & Settings

### 15.1 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/customer/profile` | Bearer | Full profile |
| PATCH | `/customer/profile` | Bearer | Update name, avatar |
| GET | `/customer/profile/stats` | Bearer | Orders, reviews, rating |
| GET | `/customer/payment-methods` | Bearer | Saved payment methods |
| POST | `/customer/payment-methods` | Bearer | Add payment method |
| DELETE | `/customer/payment-methods/:id` | Bearer | Remove payment method |
| GET | `/customer/reviews` | Bearer | Reviews written by customer |
| POST | `/customer/reviews` | Bearer | Submit a review |
| GET | `/customer/notifications/settings` | Bearer | Notification preferences |
| PATCH | `/customer/notifications/settings` | Bearer | Update notification preferences |

### 15.2 Review Schema

**POST /customer/reviews**
```json
// Request
{
  "cookId": "usr_cook1",
  "orderId": "ord_xyz789",
  "rating": 4.5,
  "comment": "Excellent biryani, delivered on time!"
}

// Response 201
{
  "id": "rev_123",
  "cookId": "usr_cook1",
  "rating": 4.5,
  "comment": "...",
  "createdAt": "2026-04-18T14:00:00Z"
}
```

---

## 16. Notifications

### 16.1 Notification Events

| Event Key | Recipient | Trigger |
|-----------|-----------|---------|
| `order.confirmed` | Customer | Payment successful |
| `order.preparing` | Customer | Cook advances to preparing |
| `order.out_for_delivery` | Customer | Cook advances to out for delivery |
| `order.delivered` | Customer | Cook marks delivered |
| `order.cancelled` | Customer | Order cancelled |
| `subscription.paused` | Customer | Subscription paused |
| `subscription.resumed` | Customer | Subscription resumed |
| `delivery.skipped` | Customer | Delivery skipped |
| `delivery.reminder` | Customer | Day before scheduled delivery |
| `new_order` | Cook | Customer places order |
| `plan.locked` | Cook | Cutoff time approaching (reminder) |
| `withdrawal.completed` | Cook | Withdrawal processed |
| `withdrawal.failed` | Cook | Withdrawal failed |
| `verification.approved` | Cook | Identity verified |
| `verification.rejected` | Cook | Identity rejected |

### 16.2 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/notifications` | Bearer | Paginated notification list |
| PATCH | `/notifications/:id/read` | Bearer | Mark single notification read |
| PATCH | `/notifications/read-all` | Bearer | Mark all read |
| GET | `/notifications/unread-count` | Bearer | Unread count badge |

---

## 17. Data Models (Full Schema)

### User
```typescript
{
  id: string                  // "usr_abc123"
  role: "customer" | "cook"
  mobile: string | null       // "+8801711000111"
  email: string | null
  displayName: string | null
  avatarUrl: string | null
  verificationStatus: "unverified" | "pending_review" | "approved" | "rejected"
  onboardingCompleted: boolean
  onboardingStep: string | null
  createdAt: string           // ISO 8601
  updatedAt: string
}
```

### Cook (extends User)
```typescript
{
  bio: string | null
  cuisineTypes: string[]
  specialties: string[]
  rating: number              // 0.0–5.0
  reviewCount: number
  totalOrdersCount: number
  areaLabel: string | null
  radiusKm: number | null
  coordinates: { lat: number; lng: number } | null
  holidayModeEnabled: boolean
  payoutMethod: "bkash" | "nagad" | "bank" | null
  payoutNumber: string | null
  payoutAccountName: string | null
  isVerified: boolean
  availableBalance: number    // BDT
}
```

### Dish
```typescript
{
  id: string
  cookId: string
  name: string
  description: string
  category: string
  mealSlot: "Breakfast" | "Lunch" | "Dinner"
  days: DayKey[]
  price: number               // BDT per portion
  capacity: number
  cutoffTime: string          // "HH:mm"
  imageUrl: string | null
  addOnsLabel: string | null
  available: boolean
  isPopular: boolean
  createdAt: string
  updatedAt: string
}
```

### Order
```typescript
{
  id: string
  customerId: string
  cookId: string
  planType: "monthly" | "today"
  items: OrderItem[]
  deliveryAddressId: string
  paymentMethod: "bkash" | "nagad" | "card"
  promoCode: string | null
  subtotal: number
  promoDiscount: number
  totalAmount: number
  status: "pending_payment" | "confirmed" | "preparing" | "packed" | "outForDelivery" | "delivered" | "cancelled"
  paymentStatus: "pending" | "paid" | "failed" | "refunded"
  placedAt: string
  updatedAt: string
}
```

### OrderItem
```typescript
{
  id: string
  orderId: string
  dishId: string
  dishName: string
  mealSlot: string
  dayLabel: string
  quantity: number
  unitPrice: number
  monthMultiplier: number
  lineTotal: number
}
```

### Subscription
```typescript
{
  id: string
  orderId: string
  customerId: string
  cookId: string
  dishId: string
  planName: string
  mealSlot: string
  portionsPerDay: number
  unitPrice: number
  monthlyTotal: number
  status: "active" | "paused" | "cancelled"
  pausedUntil: string | null
  pausedPortions: number
  startDate: string
  endDate: string
  createdAt: string
  updatedAt: string
}
```

### DeliveryInstance
```typescript
{
  id: string
  subscriptionId: string
  customerId: string
  cookId: string
  date: string                // "YYYY-MM-DD"
  status: "scheduled" | "delivered" | "skipped" | "skipped_paused"
  quantityOrdered: number
  quantityDelivered: number
  quantitySkipped: number
  deliveredAt: string | null
  skippedAt: string | null
  undoableUntil: string | null
}
```

### DemandItem
```typescript
{
  id: string
  cookId: string
  dishId: string
  dishName: string
  mealSlot: string
  date: string
  cutoffTime: string
  baseline: number
  oneOff: number
  overrides: number
  cancellations: number
  capacity: number
  isLocked: boolean
  lockedAt: string | null
  productionStatus: "pending" | "preparing" | "packed" | "outForDelivery" | "delivered"
  contributions: DemandContribution[]
}
```

### DemandContribution
```typescript
{
  id: string
  demandItemId: string
  customerId: string
  orderId: string
  customerName: string
  companyName: string | null
  deliveryAddress: string
  phoneNumber: string | null
  quantity: number
  type: "Subscription" | "One-off" | "Override" | "Cancellation"
  isDelivered: boolean
  deliveredAt: string | null
}
```

---

## 18. API Endpoint Reference

### Base URL
```
https://api.khabar.app/v1
```

### Authentication Header
```
Authorization: Bearer <accessToken>
```

### Complete Endpoint List

| Method | Path | Auth | Module |
|--------|------|------|--------|
| POST | `/auth/otp/send` | None | Auth |
| POST | `/auth/otp/verify` | None | Auth |
| POST | `/auth/token/refresh` | None | Auth |
| POST | `/auth/logout` | Bearer | Auth |
| PATCH | `/cook/onboarding/name` | Bearer | Cook Onboarding |
| PATCH | `/cook/onboarding/profile` | Bearer | Cook Onboarding |
| PATCH | `/cook/onboarding/specialties` | Bearer | Cook Onboarding |
| PATCH | `/cook/onboarding/service-area` | Bearer | Cook Onboarding |
| POST | `/cook/onboarding/identity` | Bearer | Cook Onboarding |
| PATCH | `/cook/onboarding/payout` | Bearer | Cook Onboarding |
| POST | `/cook/onboarding/complete` | Bearer | Cook Onboarding |
| GET | `/cook/onboarding/status` | Bearer | Cook Onboarding |
| GET | `/cook/profile` | Bearer | Cook Profile |
| PATCH | `/cook/profile` | Bearer | Cook Profile |
| PATCH | `/cook/profile/holiday-mode` | Bearer | Cook Profile |
| GET | `/cook/profile/stats` | Bearer | Cook Profile |
| GET | `/cook/verification` | Bearer | Cook Profile |
| PATCH | `/cook/service-area` | Bearer | Cook Profile |
| PATCH | `/cook/payout` | Bearer | Cook Profile |
| GET | `/cook/menu` | Bearer | Cook Menu |
| POST | `/cook/menu/dishes` | Bearer | Cook Menu |
| PATCH | `/cook/menu/dishes/:dishId` | Bearer | Cook Menu |
| DELETE | `/cook/menu/dishes/:dishId` | Bearer | Cook Menu |
| PATCH | `/cook/menu/dishes/:dishId/availability` | Bearer | Cook Menu |
| GET | `/cook/demand` | Bearer | Cook Orders |
| POST | `/cook/demand/:demandItemId/lock` | Bearer | Cook Orders |
| PATCH | `/cook/demand/:demandItemId/status` | Bearer | Cook Orders |
| PATCH | `/cook/demand/:demandItemId/contributions/:cId/delivered` | Bearer | Cook Orders |
| GET | `/cook/earnings/summary` | Bearer | Cook Earnings |
| GET | `/cook/earnings/trend` | Bearer | Cook Earnings |
| GET | `/cook/earnings/transactions` | Bearer | Cook Earnings |
| POST | `/cook/earnings/withdraw` | Bearer | Cook Earnings |
| GET | `/cook/earnings/withdrawals` | Bearer | Cook Earnings |
| GET | `/cooks` | Bearer | Discovery |
| GET | `/cooks/trending` | Bearer | Discovery |
| GET | `/cooks/nearby` | Bearer | Discovery |
| GET | `/cooks/search` | Bearer | Discovery |
| GET | `/cooks/:cookId` | Bearer | Cook Detail |
| GET | `/cooks/:cookId/menu` | Bearer | Cook Detail |
| GET | `/cooks/:cookId/reviews` | Bearer | Cook Detail |
| GET | `/categories` | Bearer | Discovery |
| GET | `/cart` | Bearer | Cart |
| POST | `/cart/items` | Bearer | Cart |
| PATCH | `/cart/items/:rowId` | Bearer | Cart |
| DELETE | `/cart/items/:rowId` | Bearer | Cart |
| DELETE | `/cart` | Bearer | Cart |
| POST | `/cart/promo` | Bearer | Cart |
| DELETE | `/cart/promo` | Bearer | Cart |
| GET | `/checkout/summary` | Bearer | Checkout |
| POST | `/orders` | Bearer | Orders |
| GET | `/customer/orders` | Bearer | Customer Orders |
| GET | `/customer/orders/:orderId` | Bearer | Customer Orders |
| POST | `/customer/orders/:orderId/cancel` | Bearer | Customer Orders |
| POST | `/customer/orders/:orderId/reorder` | Bearer | Customer Orders |
| GET | `/customer/subscriptions` | Bearer | Subscriptions |
| GET | `/customer/subscriptions/:subId` | Bearer | Subscriptions |
| GET | `/customer/subscriptions/:subId/calendar` | Bearer | Subscriptions |
| POST | `/customer/subscriptions/:subId/pause` | Bearer | Subscriptions |
| POST | `/customer/subscriptions/:subId/resume` | Bearer | Subscriptions |
| POST | `/customer/subscriptions/:subId/cancel` | Bearer | Subscriptions |
| POST | `/customer/subscriptions/:subId/deliveries/:dId/skip` | Bearer | Subscriptions |
| POST | `/customer/subscriptions/:subId/deliveries/:dId/resume` | Bearer | Subscriptions |
| GET | `/customer/profile` | Bearer | Customer Profile |
| PATCH | `/customer/profile` | Bearer | Customer Profile |
| GET | `/customer/addresses` | Bearer | Addresses |
| POST | `/customer/addresses` | Bearer | Addresses |
| PATCH | `/customer/addresses/:id` | Bearer | Addresses |
| DELETE | `/customer/addresses/:id` | Bearer | Addresses |
| PATCH | `/customer/addresses/:id/default` | Bearer | Addresses |
| GET | `/customer/payment-methods` | Bearer | Payments |
| POST | `/customer/payment-methods` | Bearer | Payments |
| DELETE | `/customer/payment-methods/:id` | Bearer | Payments |
| POST | `/customer/reviews` | Bearer | Reviews |
| GET | `/notifications` | Bearer | Notifications |
| PATCH | `/notifications/:id/read` | Bearer | Notifications |
| PATCH | `/notifications/read-all` | Bearer | Notifications |
| GET | `/notifications/unread-count` | Bearer | Notifications |
| POST | `/webhooks/payment` | HMAC | Webhooks |

---

## 19. State Machine Definitions

### Order Status
```
pending_payment ──(payment success)──► confirmed
pending_payment ──(payment fail)────► cancelled
confirmed ───────(cook: preparing)──► preparing
preparing ───────(cook: packed)─────► packed
packed ──────────(cook: outForDel.)─► outForDelivery
outForDelivery ──(all delivered)────► delivered
confirmed ───────(customer cancel)──► cancelled  [only before cutoff]
```

### Production Status (DemandItem)
```
pending ──(lock + start)──► preparing
preparing ────────────────► packed
packed ───────────────────► outForDelivery
outForDelivery ───────────► delivered
```

### Subscription Status
```
active ──(pause)──► paused
paused ──(resume)─► active
active ──(cancel)─► cancelled
paused ──(cancel)─► cancelled
```

### DeliveryInstance Status
```
scheduled ──(customer skip)────► skipped
scheduled ──(subscription pause)► skipped_paused
scheduled ──(cook delivers)────► delivered
skipped ───(customer undo)─────► scheduled  [before undoableUntil]
```

### Cook Verification
```
unverified ──(submit docs)──► pending_review
pending_review ─(approve)──► approved
pending_review ─(reject)───► rejected
rejected ───────(resubmit)─► pending_review
```

### Withdrawal Status
```
processing ──(success)──► completed
processing ──(fail)─────► failed
failed ─────(retry)─────► processing
```

---

## 20. Error Codes & Responses

### Standard Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": {}
  }
}
```

### HTTP Status Codes Used

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (async, e.g. withdrawal) |
| 204 | No Content (e.g. logout, delete) |
| 400 | Bad Request / Validation Error |
| 401 | Unauthorized — missing or expired token |
| 403 | Forbidden — authenticated but not allowed |
| 404 | Resource not found |
| 409 | Conflict (e.g. duplicate, already exists) |
| 410 | Gone (e.g. promo code expired) |
| 422 | Unprocessable — business rule violation |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

### Application Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| `OTP_INVALID` | 400 | OTP code is wrong |
| `OTP_EXPIRED` | 400 | OTP code has expired |
| `OTP_TOO_MANY_ATTEMPTS` | 429 | Too many OTP attempts |
| `OTP_COOLDOWN` | 429 | Resend too soon |
| `TOKEN_EXPIRED` | 401 | Access token expired |
| `TOKEN_INVALID` | 401 | Token malformed/invalid |
| `ONBOARDING_INCOMPLETE` | 403 | User hasn't completed onboarding |
| `COOK_NOT_VERIFIED` | 403 | Cook identity not approved |
| `COOK_ON_HOLIDAY` | 422 | Cook in holiday mode, orders blocked |
| `DISH_NOT_AVAILABLE` | 422 | Dish marked unavailable |
| `CAPACITY_EXCEEDED` | 422 | Dish at full capacity for the day |
| `CUTOFF_PASSED` | 422 | Order cutoff time has passed |
| `PLAN_ALREADY_LOCKED` | 409 | DemandItem already locked |
| `INVALID_STATUS_TRANSITION` | 422 | Production status out of order |
| `PROMO_INVALID` | 400 | Promo code not found |
| `PROMO_EXPIRED` | 410 | Promo code expired |
| `PROMO_ALREADY_USED` | 409 | Promo code already redeemed |
| `SUBSCRIPTION_NOT_ACTIVE` | 422 | Cannot pause/skip inactive subscription |
| `DELIVERY_NOT_SKIPPABLE` | 422 | Delivery already delivered or past undo window |
| `PAYMENT_FAILED` | 422 | Payment gateway returned failure |
| `INSUFFICIENT_BALANCE` | 422 | Withdrawal amount exceeds available balance |
| `ADDRESS_NOT_FOUND` | 404 | Delivery address ID not found |
| `ORDER_NOT_CANCELLABLE` | 422 | Order past cancellable state |

---

*End of SRS — Khabar v1.0*
