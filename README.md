# Matrimony Application - FastAPI Backend

A complete, feature-rich FastAPI backend developed for a premium matrimony application. It integrates user authentication, comprehensive user profiles, interactions (interests, visits, contact views, blocking, passing, favourites, and private notes), real-time chat/requests/calls logs, and membership management (Silver, Gold, Platinum subscription quotas).

> 💡 **Production Deployment**: See [HOSTING.md](./HOSTING.md) for the low-cost cloud hosting strategy (Oracle Cloud Free Tier, Cloudflare Pages/R2, Hetzner, and Expo EAS).

---

## Architecture & Directory Layout

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI initialization, CORS, router bindings
│   ├── config.py          # Pydantic Settings configuration from .env
│   ├── database.py        # SQLAlchemy engine and SessionLocal setup
│   ├── models/            # SQLAlchemy database schemas
│   │   ├── __init__.py
│   │   ├── user.py        # Account, membership details, verification status
│   │   ├── profile.py     # Profile categories, physical, religious, partner preferences
│   │   ├── interaction.py # Interests, visits, contact views, favourites, blocks, notes, passes
│   │   └── chat.py        # Chats, requests, and call log histories
│   ├── schemas/           # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── interaction.py
│   │   └── chat.py
│   ├── routers/           # API endpoints (endpoints return JSON/schemas)
│   │   ├── __init__.py
│   │   ├── auth.py        # Registration, login, identity verification
│   │   ├── profile.py     # Matches matching, photos, custom profile search
│   │   ├── explore.py     # Interests, visits, contact views, blocks, notes
│   │   ├── inbox.py       # Message exchanges, call logs, online-only filtering
│   │   └── menu.py        # Membership plans, renewal, billing, notifications
│   └── utils/
│       ├── __init__.py
│       ├── security.py    # BCrypt hashing, JWT token operations
│       └── deps.py        # Session auth & active state updater dependency
├── requirements.txt       # Project dependencies
├── docker-compose.yml     # Standalone PostgreSQL database
└── seed.py                # Database tables builder & dummy mock data loader
```

---

## Getting Started (Docker Compose)

### 1. Build and Start the Application
You can build and spin up both the PostgreSQL database and the FastAPI application using Docker Compose:
```bash
docker compose up -d --build
```
This starts:
- **FastAPI Backend (`web`):** Running on port `8000`
- **PostgreSQL Database (`db`):** Running internally for the web container and mapped to port `5435` on your host.

### 2. Seed the Database
Run the seed script directly inside the running FastAPI container to create tables and populate them with sample data (users, matches, photos, notes, interests, and chats):
```bash
docker compose exec web python seed.py
```

### 3. Access API Documentation
Once started, navigate to:
* **Interactive OpenAPI docs (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Alternative API docs (Redoc):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Local Development (Optional)
If you prefer to run the FastAPI app locally outside of Docker (while keeping PostgreSQL in Docker):

1. Start only the database: `docker compose up -d db`
2. Create and activate a python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the seed script: `python seed.py`
4. Start the development server: `uvicorn app.main:app --reload`


---

## Detailed API Specifications

### 🔑 Authentication (`/api/auth`)
* `POST /api/auth/register`: Register email + password (automatically creates default Profile).
* `POST /api/auth/login`: Form login returning bearer JWT access token.
* `GET /api/auth/me`: Get current logged-in user's details and active state.
* `POST /api/auth/verify-id`: Submit verification document (sets status to "Pending").

### 👤 Profiles & Matches (`/api/profiles`)
* `GET /api/profiles/me`: Preview my own profile.
* `PUT /api/profiles/me`: Update profile (supports partial updates of educational, physical, lifestyle, socio-religious details, etc.).
* `GET /api/profiles/matches`: Get matching profiles opposite to user's gender. Supports `category` query param:
  - `my_matches`: Matches based on partner preferences (age, height, religion).
  - `new_matches`: Profiles registered in the last 7 days.
  - `location`: Profiles sharing the user's city/present location.
  - `profession`: Profiles sharing the user's job sector/profession.
  - `differently_abled`: Profiles marked as differently abled.
  - `orphan_poor_girls`: Profiles flagged in the orphan or poor girls category.
* `GET /api/profiles/search`: Custom search filter query (age ranges, religion, sect, location, profession, differently abled).
* `GET /api/profiles/{profile_id}`: View specific profile (automatically registers a **Profile Visit**).
* `POST /api/profiles/photos`: Upload a photo URL (can designate as `is_main`).
* `GET /api/profiles/photos`: View list of uploaded photos.
* `DELETE /api/profiles/photos/{photo_id}`: Delete an uploaded photo.

### 🧭 Explore & Interactions (`/api/explore`)
* `POST /api/explore/interests`: Send connection interest request to another profile.
* `GET /api/explore/interests/received`: List received interest requests.
* `GET /api/explore/interests/sent`: List sent interest requests.
* `PUT /api/explore/interests/{interest_id}`: Accept/Decline a received interest.
* `GET /api/explore/visits/my-visitors`: View users who visited my profile.
* `GET /api/explore/visits/visited-by-me`: View profiles I visited.
* `POST /api/explore/contact-views/{target_user_id}`: Request contact details. *Decrements remaining views quota; returns 403 if quota is 0.*
* `GET /api/explore/contact-views/viewed-by-me`: List profiles whose contacts I viewed.
* `GET /api/explore/contact-views/my-viewers`: List users who viewed my contact info.
* `POST /api/explore/favourites`: Add profile to favourites.
* `GET /api/explore/favourites`: Get favourited profiles.
* `DELETE /api/explore/favourites/{target_user_id}`: Remove profile from favourites.
* `POST /api/explore/notes`: Add or update a private note about a profile.
* `GET /api/explore/notes/{profile_id}`: Get my private note about a profile.
* `DELETE /api/explore/notes/{note_id}`: Delete a private note.
* `POST /api/explore/blocked`: Block a user (hides profile and removes all mutual interest/favourite logs).
* `GET /api/explore/blocked`: List blocked users.
* `DELETE /api/explore/blocked/{target_user_id}`: Unblock a user.
* `POST /api/explore/passed`: Pass (hide) a user from main matches.
* `GET /api/explore/passed`: List passed profiles.

### 📥 Inbox & Messages (`/api/inbox`)
* `POST /api/inbox/messages`: Send chat message, request, or call log. *Free accounts check message limits; call logs check remaining call time balance.*
* `GET /api/inbox/conversations`: Get list of unique conversations (includes last message, unread count, participant info, and online status).
* `GET /api/inbox/conversations/{participant_id}`: Get complete message timeline history. Marks unread messages as read.
* `GET /api/inbox/all`: List messages with optional `online_now=true` query filter.
* `GET /api/inbox/chats`: List messages of type `chat` with `online_now=true` query filter.
* `GET /api/inbox/requests`: List connection requests with `online_now=true` query filter.
* `GET /api/inbox/calls`: List calls logs with `online_now=true` query filter.

### ⚙️ Sidebar Menu & Subscriptions (`/api/menu`)
* `GET /api/menu/summary`: Returns sidebar info: Name, ID, membership status, plan type, remaining contact views, remaining message credits, remaining call minutes, and validity.
* `POST /api/menu/subscribe`: Subscribe/Upgrade plan (Silver, Gold, or Platinum). replenishes communication quotas and sets expiration datetime.
* `POST /api/menu/renew`: Renew/extend the current plan.
* `PUT /api/menu/settings`: Modify user credentials (email, password, activation state).
* `GET /api/menu/notifications`: View system announcements/notifications.
* `POST /api/menu/link-device`: Pair a secondary web device using a shortcode.
* `POST /api/menu/feedback`: Submit application rating and comments.
* `GET /api/menu/support`: View support contacts and FAQ.
