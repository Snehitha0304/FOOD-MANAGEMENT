# Mandatory Security Controls & Architecture

This backend demonstrates all 10 mandatory security controls outlined in the evaluation criteria:

### 1. Password Hashing
- **Control:** Passwords hashed with standard adaptive bcrypt hashing via `passlib[bcrypt]`.
- **Implementation:** `app/core/security.py` uses `CryptContext(schemes=["bcrypt"], deprecated="auto")`. Plaintext passwords are never stored or logged.

### 2. JWT Authentication
- **Control:** Secure token generation and verification using `python-jose`. Tokens contain `sub` (User ID string) and `role`, signed with secret key (`HS256`) and configurable expiry (`ACCESS_TOKEN_EXPIRE_MINUTES`, default 30 min).
- **Implementation:** `create_access_token` and `decode_access_token` in `app/core/security.py`.

### 3. Role-Based Access Control (RBAC)
- **Control:** Declarative, reusable FastAPI dependency `require_role(*roles)` securing all routes based on the 4 application roles:
  - `ADMIN`
  - `RESTAURANT_OWNER`
  - `CUSTOMER`
  - `DELIVERY_AGENT`
- **Implementation:** `app/core/security.py` and modular dependencies in `app/dependencies/`. Tested in `tests/security/test_rbac.py`.

### 4. Ownership Checks & IDOR Prevention
- **Control:** Users cannot read or modify another user's resources by tampering with IDs in URLs or request payloads.
- **Enforcement:**
  - Addresses & Profile: Customers can only manage their own addresses (`tests/test_customer.py`).
  - Menu Items: A restaurant owner cannot edit or delete another owner's menu items (`tests/ownership/test_owner_cannot_edit_other_menu.py`).
  - Orders: `GET /orders/{id}` enforces participant-only access (ordering customer, receiving restaurant owner, assigned delivery agent, or admin). Tested in `tests/security/test_order_access.py`.

### 5. Input Validation & Type Safety
- **Control:** Strict Pydantic v2 schemas for all request payloads, query parameters, and path variables. Field constraints include length limits, regex patterns (phones, pincodes), numeric ranges, and enum validations. No raw dictionaries accepted.

### 6. SQL-Injection Safety
- **Control:** Strict use of SQLAlchemy 2.0 ORM and parameterized query expressions (`select()`, `where()`, `func.count()`). Zero raw or f-string SQL queries exist anywhere in the codebase.

### 7. Secret Management
- **Control:** Database credentials, JWT secrets, algorithm, and business rules are loaded from environment variables using `pydantic-settings`. `.env` is git-ignored, and `.env.example` is committed.

### 8. Safe Error Handling
- **Control:** Global exception handlers format all errors as structured JSON:
  ```json
  {
    "detail": "Error description message",
    "code": "ERROR_CODE"
  }
  ```
  Internal server errors and database exceptions suppress stack traces and raw SQL from leaking to clients.

### 9. Audit-Friendly Structured Logging
- **Control:** Structured application and audit logging via `logging.getLogger("audit")`. Records all authentication attempts, user registrations, and state transitions with user ID and UTC timestamp. Passwords, authorization tokens, and secrets are strictly excluded from logs.

### 10. CORS & Rate Limiting
- **Control:**
  - CORS middleware configured via `Settings.CORS_ORIGINS`.
  - IP-based rate limiting on sensitive authentication endpoints via `SlowAPI` (`RATE_LIMIT_LOGIN="10/minute"`).

### Special Privacy Feature: Delivery Agent Customer Phone Masking
- **Requirement:** Customer phone numbers must be exposed to the delivery agent **only after the order reaches `PICKED_UP`**.
- **Implementation:** In `OrderService.get_order_detail`, if the caller is a `DELIVERY_AGENT` and the order status is `READY_FOR_PICKUP` or earlier, `customer_phone` is masked as `null`. As soon as status transitions to `PICKED_UP` or `DELIVERED`, the customer's phone number is revealed. Tested in `tests/test_delivery.py`.
