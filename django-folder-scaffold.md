# 🏗️ KHABAR — Django Backend Scaffold (Production Architecture)

---

# 📁 1. ROOT PROJECT STRUCTURE

```bash
khabar-backend/
│
├── config/                         # Django project settings
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py                 # shared settings
│   │   ├── dev.py                  # development
│   │   ├── prod.py                 # production
│   │
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│
├── apps/                           # ALL business apps
│
├── core/                           # system-wide base logic
│   ├── models.py                   # BaseModel, TimeStampedModel
│   ├── services.py                 # BaseService
│   ├── exceptions.py               # ServiceException
│   ├── permissions.py
│   ├── pagination.py
│   ├── utils.py
│
├── shared/                         # shared helpers
│   ├── constants/
│   ├── validators/
│   ├── helpers/
│   ├── enums/
│
├── tests/                          # global integration tests
│
├── manage.py
├── requirements.txt
├── .env
└── README.md
```

---

# 📦 2. APPS STRUCTURE (FEATURE-BASED)

```bash
apps/
│
├── auth/
├── users/
├── cooks/
├── customers/
├── menu/
├── orders/
├── subscriptions/
├── payments/
├── notifications/
├── reviews/
├── locations/
```

---

# 🍽️ 3. APP INTERNAL STRUCTURE (STANDARD TEMPLATE)

Every app MUST follow this exact structure:

```bash
orders/
│
├── models/
│   ├── order.py
│   ├── order_item.py
│   ├── __init__.py
│
├── serializers/
│   ├── order_serializer.py
│
├── views/
│   ├── order_viewset.py
│
├── services/
│   ├── create_order_service.py
│   ├── cancel_order_service.py
│   ├── order_price_service.py
│
├── selectors/                      # read/query optimization layer
│   ├── order_selector.py
│
├── urls.py
├── permissions.py
├── exceptions.py
├── constants.py
├── admin.py
└── tests/
```

---

# 🔐 4. AUTH APP STRUCTURE (OTP SYSTEM)

```bash
auth/
│
├── models/
│   ├── otp.py
│
├── services/
│   ├── otp_service.py
│   ├── auth_service.py
│   ├── token_service.py
│
├── serializers/
│   ├── otp_send_serializer.py
│   ├── otp_verify_serializer.py
│
├── views/
│   ├── auth_viewset.py
│
├── urls.py
└── exceptions.py
```

---

# 👤 5. USERS APP (CORE USER MODEL)

```bash
users/
│
├── models/
│   ├── user.py                # CustomUser (single source of truth)
│   ├── profile.py
│
├── services/
│   ├── user_service.py
│
├── serializers/
│   ├── user_serializer.py
│
├── views/
│   ├── user_viewset.py
│
├── urls.py
└── admin.py
```

---

# 👨‍🍳 6. COOKS APP

```bash
cooks/
│
├── models/
│   ├── cook_profile.py
│   ├── verification.py
│   ├── payout_account.py
│
├── services/
│   ├── onboarding_service.py
│   ├── verification_service.py
│
├── serializers/
│   ├── cook_profile_serializer.py
│   ├── onboarding_serializer.py
│
├── views/
│   ├── cook_profile_viewset.py
│   ├── onboarding_viewset.py
│
├── urls.py
└── selectors/
```

---

# 🍱 7. MENU APP

```bash
menu/
│
├── models/
│   ├── dish.py
│   ├── weekly_menu.py
│
├── services/
│   ├── dish_service.py
│   ├── menu_builder_service.py
│
├── serializers/
│   ├── dish_serializer.py
│
├── views/
│   ├── menu_viewset.py
│
├── selectors/
│   ├── menu_selector.py
│
└── urls.py
```

---

# 📦 8. ORDERS APP (CORE ENGINE)

```bash
orders/
│
├── models/
│   ├── order.py
│   ├── order_item.py
│   ├── order_status_history.py
│
├── services/
│   ├── create_order_service.py
│   ├── cancel_order_service.py
│   ├── order_transition_service.py
│   ├── price_calculation_service.py
│
├── selectors/
│   ├── order_selector.py
│
├── serializers/
│   ├── order_create_serializer.py
│   ├── order_detail_serializer.py
│
├── views/
│   ├── order_viewset.py
│
├── urls.py
└── exceptions.py
```

---

# 🔁 9. SUBSCRIPTIONS APP (VERY IMPORTANT)

```bash
subscriptions/
│
├── models/
│   ├── subscription.py
│   ├── delivery_instance.py
│
├── services/
│   ├── subscription_service.py
│   ├── pause_service.py
│   ├── delivery_generator_service.py
│
├── selectors/
│   ├── subscription_selector.py
│
├── views/
│   ├── subscription_viewset.py
│
├── urls.py
```

---

# 💰 10. PAYMENTS APP

```bash
payments/
│
├── models/
│   ├── payment.py
│   ├── withdrawal.py
│
├── services/
│   ├── payment_service.py
│   ├── withdrawal_service.py
│   ├── webhook_service.py
│
├── views/
│   ├── payment_viewset.py
│
├── urls.py
└── webhooks.py
```

---

# 🔔 11. NOTIFICATIONS APP (EVENT-BASED)

```bash
notifications/
│
├── models/
│   ├── notification.py
│
├── services/
│   ├── notification_service.py
│   ├── event_dispatcher.py
│
├── events/
│   ├── order_events.py
│   ├── subscription_events.py
│
├── views/
│   ├── notification_viewset.py
│
├── urls.py
```

---

# 🧠 12. CORE MODULE (VERY IMPORTANT)

```bash
core/
│
├── models.py
│   ├── BaseModel
│   ├── TimeStampedModel
│
├── services.py
│   ├── BaseService
│
├── exceptions.py
│   ├── ServiceException
│
├── pagination.py
├── permissions.py
├── utils.py
└── validators.py
```

---

# ⚙️ 13. CONFIG SETUP FLOW

## settings/base.py includes:

* Django REST Framework
* Simple JWT
* PostgreSQL
* CORS
* Redis (future caching)
* Celery (future async jobs)

---

# 🔌 14. URL STRUCTURE

```bash
/api/v1/auth/
/api/v1/users/
/api/v1/cooks/
/api/v1/menu/
/api/v1/orders/
/api/v1/subscriptions/
/api/v1/payments/
/api/v1/notifications/
```

---

# 🚨 15. IMPORTANT DESIGN RULES (CRITICAL)

### ❌ NEVER:

* put business logic in views
* directly update order status in models
* duplicate service logic across apps
* mix subscription logic inside orders app

---

### ✅ ALWAYS:

* use services for all logic
* use selectors for read queries
* keep models dumb
* keep views thin

---

# 🧠 FINAL RESULT (WHAT YOU NOW HAVE)

This structure gives you:

### ✔ scalable architecture like Swiggy/Zomato

### ✔ clean service-based backend

### ✔ separation of read/write logic

### ✔ production-ready modular design

### ✔ easy AI-agent coding compatibility

---
