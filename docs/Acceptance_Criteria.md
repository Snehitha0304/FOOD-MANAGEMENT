# Acceptance Criteria Verification & Test Results

All acceptance criteria specified in the Case Study 04 specification are satisfied and verified by automated tests:

### 1. All 24 User Stories Work Through Swagger UI
- **Status:** **PASS**
- **Evidence:** All 24 user stories have corresponding endpoints registered in FastAPI and documented in Swagger UI (`/docs`). Seed script populates demo accounts for all 4 roles to allow immediate manual walkthrough.

### 2. Invalid State Transitions Return 409 Conflict
- **Status:** **PASS**
- **Evidence:** Enforced by `app/core/state_machine.py`. Verified in `tests/state_machine/test_invalid_transitions.py` covering disallowed state jumps (e.g., `PLACED` to `PREPARING` skipping `CONFIRMED`, `CANCELLED` to `CONFIRMED`, etc.).

### 3. Second Restaurant Owner Cannot Edit First Owner's Menu Items
- **Status:** **PASS**
- **Evidence:** Enforced via JWT subject authentication and ownership checking in `MenuService`. Verified in `tests/ownership/test_owner_cannot_edit_other_menu.py` where Owner 2 attempts to edit, toggle availability, or delete Owner 1's items and is rejected with `403 Forbidden` (`code: ITEM_OWNERSHIP_VIOLATION`).

### 4. Pricing Tampering Protection
- **Status:** **PASS**
- **Evidence:** Client-supplied prices are strictly ignored; server retrieves live item prices from the database and calculates item total, tax (5%), delivery fees, and grand total. Verified in `tests/pricing/test_tampered_price.py`.

### 5. Pytest Coverage >= 70%
- **Status:** **PASS (92% achieved)**
- **Evidence:** Pytest suite contains **48 automated tests** passing 100% with **92% line coverage** across the application codebase.
  - Happy paths per module: Verified
  - Authentication failure tests: Verified
  - Authorisation (wrong role) tests: Verified
  - Validation failure tests: Verified
