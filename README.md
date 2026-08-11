# HelpMeet Matrimony Application - FastAPI Backend

A complete, feature-rich FastAPI backend developed for **HelpMeet** - a premium matrimony application. It integrates user authentication, comprehensive user profiles, dynamic match discovery, interactions (interests, visits, contact views, blocking, passing, favourites, and private notes), real-time chat/requests/calls logs, membership quota management (Silver, Gold, Platinum plans), and an Administrative Console for user identity and photo validation.

> 💡 **Production Deployment**: See [HOSTING.md](./HOSTING.md) for the low-cost cloud hosting strategy (Oracle Cloud Free Tier, Cloudflare Pages/R2, Hetzner, and Expo EAS).

---

## 🏗️ Architecture & Directory Layout

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI initialization, CORS, router bindings
│   ├── config.py          # Pydantic Settings configuration from .env
│   ├── database.py        # SQLAlchemy engine, SessionLocal, and auto-migrations
│   ├── models/            # SQLAlchemy database schemas
│   │   ├── __init__.py
│   │   ├── user.py        # Account, admin role, membership details, verification status
│   │   ├── profile.py     # Profile categories, physical, religious, partner preferences
│   │   ├── interaction.py # Interests, visits, contact views, favourites, blocks, notes, passes
│   │   └── chat.py        # Chats, requests, and call log histories
│   ├── schemas/           # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── interaction.py
│   │   └── chat.py
│   ├── routers/           # API endpoints (return JSON/schemas)
│   │   ├── __init__.py
│   │   ├── auth.py        # Registration, login, identity verification
│   │   ├── profile.py     # Matches, photo uploads, custom profile search
│   │   ├── explore.py     # Interests, visits, contact views, blocks, notes
│   │   ├── inbox.py       # Message exchanges, call logs, online-only filtering
│   │   ├── menu.py        # Subscription plans, renewal, billing, notifications
│   │   └── admin.py      # Admin verification endpoints for ID docs and photos
│   └── utils/
│       ├── __init__.py
│       ├── security.py    # BCrypt hashing, JWT token operations
│       └── deps.py        # Session auth & active state updater dependency
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Standalone PostgreSQL database & web app
└── seed.py                # Database tables builder & dummy mock data loader
```

---

## 💳 Subscriptions & Dynamic Quota System

Subscriptions replenish user contact view credits, messaging balance, call minutes, and validity:

* **Silver Plan**: **₹299** (20 Contact Views, 200 Messages, 60 Call Mins, 30 Days Validity)
* **Gold Plan**: **₹1,299** (100 Contact Views, 1000 Messages, 300 Call Mins, 90 Days Validity)
* **Platinum Plan**: **₹2,499** (9999 Contact Views, 9999 Messages, 1000 Call Mins, 180 Days Validity)

---

## 🚀 Getting Started (Docker Compose)

### 1. Build and Start the Application
Spin up both the PostgreSQL database and the FastAPI backend:
```bash
docker compose up -d --build
```
- **FastAPI Backend (`web`):** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **PostgreSQL Database (`db`):** Mapped internally and exposed on port `5435`.

### 2. Seed the Database
Run the seed script inside the running container to initialize tables and sample data:
```bash
docker compose exec web python seed.py
```

### 3. Access API Documentation
* **Interactive OpenAPI docs (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Alternative API docs (Redoc):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔑 Default Test Accounts

- **Admin Account**: `admin@matrimony.com` / `admin123`
- **Male User**: `ahmed@example.com` / `password123`
- **Female User**: `fatima@example.com` / `password123`

---

## 🛡️ Detailed API Specifications

### 🔑 Authentication (`/api/auth`)
* `POST /api/auth/register`: Register email + password.
* `POST /api/auth/login`: Form login returning JWT token.
* `GET /api/auth/me`: Get current logged-in user details.
* `POST /api/auth/verify-id`: Submit verification document (sets status to "Pending").

### 👤 Profiles & Matches (`/api/profiles`)
* `GET /api/profiles/me`: Preview my own profile.
* `PUT /api/profiles/me`: Update profile details.
* `GET /api/profiles/matches`: Get matching profiles (opposite gender).
* `GET /api/profiles/search`: Custom search filter query (age, religion, sect, location, profession).
* `POST /api/profiles/photos`: Upload a photo. Defaults to `is_approved = False` for admin verification.
* `GET /api/profiles/photos`: View list of uploaded photos.
* `DELETE /api/profiles/photos/{photo_id}`: Delete an uploaded photo.

### 🧭 Explore & Interactions (`/api/explore`)
* `POST /api/explore/interests`: Send connection interest request.
* `GET /api/explore/interests/received`: Received interest requests.
* `GET /api/explore/interests/sent`: Sent interest requests.
* `POST /api/explore/contact-views/{target_user_id}`: Unlock contact details.
* `POST /api/explore/favourites`: Add profile to favourites.
* `POST /api/explore/notes`: Add or update a private note.

### 🛡️ Admin Console & Verification (`/api/admin`)
* `GET /api/admin/pending-verifications`: List pending identity documents and unapproved profile photos.
* `POST /api/admin/verify-id/{user_id}`: Validate ID document (`{"action": "approve" | "reject"}`).
* `POST /api/admin/verify-photo/{photo_id}`: Validate profile photo (`{"action": "approve" | "reject"}`).
* `GET /api/admin/users`: Overview of all registered users and verification statuses.
