# Coderr

> **Backend** for a platform that helps companies find **professional IT talent**.  
> Built with **Django** and **Django REST Framework (DRF)**.

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.5-092E20)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.1-ff1709)](https://www.django-rest-framework.org/)

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Authentication (Token)](#authentication-token)
- [API Overview](#api-overview)
- [Example Requests](#example-requests)
- [Project Structure](#project-structure)
- [Development & Admin](#development--admin)
- [License](#license)

---

## Features

- 👥 **Profiles**: `customer` and `business`; update your own profile only
- 🧰 **Offers**: Offer + multiple **OfferDetails** (basic / standard / premium)
- 🛒 **Orders**: created from an OfferDetail, storing a **snapshot** (title, price, etc.)
- ⭐ **Reviews**: customers rate business users (1–5)
- 📊 **Stats**: basic metrics (review count, average rating, etc.)
- 🔐 **Auth**: Token-based (DRF); protected endpoints require `IsAuthenticated`

---

## Tech Stack

**Python / Django / DRF**

```
asgiref==3.9.1
Django==5.2.5
django-cors-headers==4.7.0
django-filter==25.1
djangorestframework==3.16.1
sqlparse==0.5.3
tzdata==2025.2
```

> No special environment variables required for development (SQLite by default).

---

## Architecture

```
UserProfile (AbstractUser)
  - type: "customer" | "business"
  - profile fields (file, location, tel, description, working_hours, ...)

Offer (user -> UserProfile)
  └─ OfferDetail (offer -> Offer)   [basic | standard | premium]
       - title, revisions, delivery_time_in_days, price, features, offer_type

Order
  - customer_user, business_user
  - offer_detail (FK)
  - snapshot: title, revisions, delivery_time_in_days, price, features, offer_type
  - status: in_progress | completed | cancelled

Review
  - business_user  (review target)
  - reviewer       (customer)
  - rating (1..5)
```

---

## Getting Started

### 1) Clone the project

```bash
git clone <YOUR-REPO-URL>
cd <YOUR-REPO-FOLDER>
```

### 2) Create and activate a virtual environment

**macOS / Linux**
```bash
python3 -m venv env
source env/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv env
env\Scripts\Activate
```

### 3) Install dependencies

Create a `requirements.txt` with the versions above (if not already present) and run:

```bash
pip install -r requirements.txt
```

### 4) Database migration and admin user

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5) Run the development server

```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/`

---

## Authentication (Token)

This backend uses **Token Authentication**.  
Send your token on protected endpoints:

```
Authorization: Token <YOUR_TOKEN>
```

> Obtain tokens through your auth flow (e.g., an auth app endpoint) or via Django Admin—depending on your implementation.

---

## API Overview

**Base prefix:** `/api/`

### Profiles

```text
GET   /api/profile/<pk>/                 → Retrieve single profile (public)
PATCH /api/profile/<pk>/                 → Update own profile (owner only)
GET   /api/profiles/business/            → List all business profiles (auth)
GET   /api/profiles/customer/            → List all customer profiles (auth)
```

### Offers

```text
GET   /api/offers/                       → List offers (filters such as user_id, price)
POST  /api/offers/                       → Create new offer with ≥ 3 details (business only)
GET   /api/offers/<id>/                  → Offer details (with aggregated values)
GET   /api/offerdetails/<id>/            → Single OfferDetail
```

### Orders

```text
GET    /api/orders/                                  → Orders where you are customer OR business
POST   /api/orders/                                  → Create order from OfferDetail (body: {"offer_detail_id": <int>})
PATCH  /api/orders/<id>/                             → Update status (business owner only)
DELETE /api/orders/<id>/                             → Delete (admin only)

GET    /api/order-count/<business_user_id>/         → Count in_progress for a business user
GET    /api/completed-order-count/<business_user_id>/ → Count completed for a business user
```

### Reviews

```text
GET    /api/reviews/                    → List (filters: business_user_id, reviewer_id)
POST   /api/reviews/                    → Create review (customers only)
GET    /api/rewiews/<id>/               → Single review (note: URL spelling "rewiews")
PATCH  /api/rewiews/<id>/               → Update own review
DELETE /api/rewiews/<id>/               → Delete own review
GET    /api/base-info/                  → Public basic metrics
```

> **Note:** The review detail URL is currently spelled as `rewiews`. If that is unintentional, update your URL patterns to `reviews/<int:id>/`.

---

## Example Requests

### Create an Order

```bash
curl -X POST http://127.0.0.1:8000/api/orders/   -H "Authorization: Token <TOKEN>"   -H "Content-Type: application/json"   -d '{ "offer_detail_id": 4 }'
```

**Success (201) – sample response:**
```json
{
  "id": 8,
  "customer_user": 29,
  "business_user": 28,
  "title": "Basic Design",
  "revisions": 2,
  "delivery_time_in_days": 5,
  "price": 100,
  "features": ["Logo Design", "Visitenkarte"],
  "offer_type": "basic",
  "status": "in_progress",
  "created_at": "...",
  "updated_at": "..."
}
```

### Create a Review (customers only)

```bash
curl -X POST http://127.0.0.1:8000/api/reviews/   -H "Authorization: Token <TOKEN>"   -H "Content-Type: application/json"   -d '{ "business_user": 28, "rating": 5 }'
```

---

## Project Structure

*(Excerpt—focus on main apps)*

```
auth_app/
offers_app/
  └── api/
orders_app/
  └── api/
reviews_app/
  └── api/
userprofile_app/
  └── api/
config/ (settings, urls)
manage.py
```

**Global URL include (excerpt):**
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth_app.api.urls')),
    path('api/', include('userprofile_app.api.urls')),
    path('api/', include('offers_app.api.urls')),
    path('api/', include('orders_app.api.urls')),
    path('api/', include('reviews_app.api.urls')),
]
```

**Userprofile URLs:**
```python
path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile'),
path('profiles/business/', BusinessView.as_view(), name='business'),
path('profiles/customer/', CustomerView.as_view(), name='customer'),
```

**Offers URLs:**
```python
path('offers/', OfferListView.as_view(), name='offers'),
path('offers/<int:id>/', OfferDetailsView.as_view(), name='offer-detail'),
path('offerdetails/<int:id>/', OneOfferDetailsView.as_view(), name='one-offer-details'),
```

**Orders URLs:**
```python
path('orders/', OrderListCreateView.as_view(), name='orders'),
path('orders/<int:id>/', OrderPatchView.as_view(), name='order-patch'),
path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name='order-count'),
path('completed-order-count/<int:business_user_id>/', OrderCountCompletedView.as_view(), name='order-count-completed'),
```

**Reviews URLs:**
```python
path('reviews/', ReviewsList.as_view(), name='reviews'),
path('rewiews/<int:id>/', ReviewDetail.as_view(), name='reviews-detail'),
path('base-info/', BaseInformationView.as_view(), name='base-info'),
```

---

## Development & Admin

- Admin at `http://127.0.0.1:8000/admin/`  
  (login with the superuser you created via `createsuperuser`)
- CORS / filtering prepared through `django-cors-headers` and `django-filter`.
- Tests: **none** at the moment.

---

## License

**TBD** (e.g., MIT, Apache-2.0, or proprietary).  
Please add a `LICENSE` file to your repository.

---

### Notes

- **Database**: SQLite by default for development.  
- **URL Typo** in review detail endpoints: `rewiews` → consider changing to `reviews`.  
- **Token Auth**: Ensure your auth flow issues tokens (or create tokens via Admin).

—

Happy building with **Coderr**! ✨
