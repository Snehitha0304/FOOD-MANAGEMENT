# Food Delivery Order Management System Backend (Case Study 04)

Production-grade, asynchronous REST API backend built with **Python 3.11+**, **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL** (with SQLite fallback for local test execution), **Alembic**, **Pydantic v2**, **Bcrypt**, and **JWT Authentication**.

---

## 🌟 Key Features & Architectural Highlights

1. **Deterministic Order State Machine:**
   - Enforces valid transition paths:
     - `PLACED -> CONFIRMED -> PREPARING -> READY_FOR_PICKUP -> PICKED_UP -> DELIVERED`
     - `PLACED -> REJECTED`
     - `PLACED | CONFIRMED -> CANCELLED`
   - Any invalid transition immediately returns **HTTP 409 Conflict**.
   - Every accepted status change writes an immutable audit record to `order_status_history`.

2. **Server-Side Pricing Integrity:**
   - Client-supplied prices are strictly ignored; prices are fetched directly from the database catalog.
   - Prices and item names are permanently snapshotted into `order_items` at order time to prevent historical corruption.
   - Dynamic 5% tax and configurable delivery fee thresholds (free above ₹500, else ₹40).
   - Strict `Numeric(12, 2)` monetary arithmetic (never float).

3. **Multi-Role RBAC & Participant-Only Authorization (IDOR Prevention):**
   - Four distinct roles: `ADMIN`, `RESTAURANT_OWNER`, `CUSTOMER`, `DELIVERY_AGENT`.
   - `GET /orders/{id}` is restricted to the ordering customer, the restaurant owner, the assigned agent, or an admin.
   - Restaurant owners cannot modify or delete menu items belonging to another restaurant.
   - Customer phone number is privacy-masked from the delivery agent until the order reaches `PICKED_UP`.

4. **Testing & Quality Assurance:**
   - **48 automated unit & integration tests** passing with **92% line coverage** (exceeding the 70% threshold).
   - Covers positive workflows, role authorization, state machine violations (409), IDOR prevention, and price tampering.

---

## 🏗️ Clean Layered Architecture

```
app/
├── core/                  # Core configurations, constants, security, state machine, errors
│   ├── config.py          # Pydantic Settings (.env loader)
│   ├── constants.py       # UserRole and OrderStatus Enums
│   ├── database.py        # SQLAlchemy 2.0 Engine, Base, and get_db session generator
│   ├── exceptions.py      # Structured AppException hierarchy (400, 401, 403, 404, 409, 422)
│   ├── pagination.py      # Standardized PageParams and PaginatedResponse[T]
│   ├── permissions.py     # Reusable ownership and IDOR guards
│   ├── security.py        # Passlib bcrypt hashing, JWT create/decode, require_role
│   └── state_machine.py   # State machine validator and transition rules
├── db/                    # Session & base re-exports matching guidelines
├── models/                # SQLAlchemy 2.0 ORM models (created_at, updated_at in UTC)
├── schemas/               # Pydantic v2 request/response schemas with field constraints
├── repositories/          # Pure database access queries (no business rules)
├── services/              # Pure business logic and domain orchestration (no HTTP objects)
├── routers/               # Thin FastAPI APIRouters delegating to services
├── dependencies/          # Role injection dependencies (get_current_admin, get_current_customer, etc.)
├── utils/                 # Pricing calculations, order number generator, tax helpers
└── main.py                # FastAPI app initialization, middleware, global error handlers
```

---

## 🚀 Quickstart Guide

### 1. Environment Setup
```bash
# Clone and enter directory
cd food_delivery_order_management_system

# Create virtual environment (optional if using global Python 3.11+)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```ini
DATABASE_URL=sqlite:///./food_delivery.db
# For PostgreSQL: postgresql+psycopg2://postgres:postgres@localhost:5432/food_delivery_db
JWT_SECRET_KEY=9b47e954c7d0d08bfad3c14c53880629acbd3e2e0573e8eec80f55c5dfb51234
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
TAX_PERCENTAGE=5.0
FREE_DELIVERY_THRESHOLD=500.0
DEFAULT_DELIVERY_FEE=40.0
CORS_ORIGINS=["*"]
RATE_LIMIT_LOGIN=10/minute
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 3. Run Database Migrations
Build database tables from scratch using Alembic:
```bash
alembic upgrade head
```

### 4. Seed Demo Master Data
Populate demo users for all four roles and sample restaurants, categories, menu items, and addresses:
```bash
python seed.py
```

### 5. Start Application Server
```bash
uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc API Docs: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 👥 Seeded Demo Accounts

All accounts are pre-seeded with encrypted bcrypt passwords:

| Role | Email | Password | Pre-assigned Assets |
|---|---|---|---|
| **ADMIN** | `admin@fooddelivery.com` | `Admin@123` | System-wide administrative controls |
| **RESTAURANT_OWNER** | `owner1@fooddelivery.com` | `Owner@123` | Restaurant: "Spice Junction" (Indian) |
| **RESTAURANT_OWNER** | `owner2@fooddelivery.com` | `Owner@123` | Restaurant: "Pizza Roma" (Italian) |
| **DELIVERY_AGENT** | `agent1@fooddelivery.com` | `Agent@123` | Delivery Agent ID 4 |
| **DELIVERY_AGENT** | `agent2@fooddelivery.com` | `Agent@123` | Delivery Agent ID 5 |
| **CUSTOMER** | `customer1@fooddelivery.com` | `Customer@123` | 2 Addresses in Indiranagar & Tech Park |
| **CUSTOMER** | `customer2@fooddelivery.com` | `Customer@123` | 1 Address in Whitefield |

---

## 🧪 Running Automated Tests

Run the complete test suite with coverage report:
```bash
python -m pytest
```

### Coverage Summary (92% Line Coverage)
```
Name                                        Stmts   Miss  Cover
---------------------------------------------------------------
app\core\config.py                             29      2    93%
app\core\constants.py                          15      0   100%
app\core\database.py                           20      4    80%
app\core\exceptions.py                         26      2    92%
app\core\pagination.py                         15      0   100%
app\core\security.py                           62      5    92%
app\core\state_machine.py                      13      1    92%
app\dependencies\*                             20      0   100%
app\models\*                                  169      0   100%
app\repositories\address_repository.py         30      0   100%
app\repositories\menu_repository.py            55      2    96%
app\repositories\order_repository.py           68     17    75%
app\repositories\rating_repository.py          28      6    79%
app\repositories\report_repository.py          41      0   100%
app\repositories\restaurant_repository.py      45      2    96%
app\repositories\user_repository.py            27      2    93%
app\routers\*                                 237     18    92%
app\schemas\*                                 174      0   100%
app\services\*                                479     89    81%
app\utils\*                                    25      0   100%
---------------------------------------------------------------
TOTAL                                        1601    135    92%
======================== 48 passed in 66s =====================
```

---

## 🎯 Viva Q&A Guide

#### 1. Why bcrypt and not SHA-256 for passwords?
> **Answer:** SHA-256 is a general-purpose cryptographic hash designed for high-throughput data integrity. Modern GPUs and ASICs can compute billions of SHA-256 hashes per second, making it trivial to brute-force via rainbow tables or dictionary attacks. **Bcrypt** is an adaptive, CPU- and memory-hard key-derivation function that incorporates an automatic salt and configurable work factor (rounds). This introduces controlled computational cost, rendering brute-force attacks infeasible.

#### 2. What is inside your JWT, and what happens if the secret leaks?
> **Answer:** The JWT payload contains standard claims: `sub` (user ID string), `role` (user role string), `email`, `iat` (issued-at timestamp), and `exp` (expiration timestamp, default 30 min). If the secret key leaks, an adversary can forge arbitrary JWTs with `role: "ADMIN"` or impersonate any user ID. Mitigation requires immediately revoking/rotating `JWT_SECRET_KEY` in environment variables, invalidating all existing tokens, and optionally deploying token blacklisting via a Redis cache.

#### 3. Show me how you prevent user A from reading user B's records (IDOR prevention).
> **Answer:** In `OrderService.get_order_detail`, the user's identity and role are extracted from the validated JWT subject (`current_user = Depends(get_current_user)`). The service verifies that the requester is either the `customer_id` who placed the order, the `owner_id` of the restaurant, the assigned `agent_id`, or an `ADMIN`. Any other user receives `HTTP 403 Forbidden` (`code: ORDER_ACCESS_FORBIDDEN`). Similarly, in menu item editing, ownership is verified against `restaurant.owner_id == owner_id`.

#### 4. Where would you add a database index, and why?
> **Answer:**
> - `users.email`: Unique B-Tree index for $O(\log N)$ login lookups and uniqueness enforcement.
> - `orders.order_no`: Unique index for fast human-readable order tracking lookups.
> - `orders.customer_id`, `orders.restaurant_id`, `orders.agent_id`: Foreign key indexes for rapid order filtering and history queries.
> - `orders.status`: Single/composite index for high-frequency filtering by dispatchers and restaurant owners (`status = 'PLACED'`).
> - `restaurants.city`, `restaurants.cuisine`: Indexes to optimize customer search and discovery queries.

#### 5. Which layer would you change to swap PostgreSQL for MySQL?
> **Answer:** Only the **infrastructure/configuration layer** (`app/core/config.py` and `alembic.ini`) by changing the connection string to `mysql+pymysql://...`. Because the application is strictly partitioned into ORM models, generic repositories using SQLAlchemy 2.0 expressions, and clean domain services with zero raw SQL, the business logic and routers require **zero code changes**.

#### 6. How does FastAPI's dependency injection help your testing?
> **Answer:** FastAPI's `app.dependency_overrides` mechanism allows seamless swapping of production dependencies with mock or test fixtures without monkey-patching. In our pytest suite (`tests/conftest.py`), `get_db` is overridden with an in-memory SQLite testing session with `StaticPool`, providing total isolation, high-speed execution, and automatic rollback between tests.
