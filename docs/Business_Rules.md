# Business Rules & Implementation Details

The system enforces 8 explicit core business rules, embedded within the Service and Utility layers:

### 1. Server-Side Price & Total Calculation
- **Rule:** Prices and totals are always computed on the server from current menu prices; any client-supplied price is completely ignored.
- **Implementation:** `app/services/order_service.py` queries `MenuItem` prices from the database for each submitted item ID and ignores any `price` field sent by the client. Tested in `tests/pricing/test_tampered_price.py`.

### 2. Historical Snapshotting in Order Items
- **Rule:** Item name and unit price are snapshotted into `order_items` so subsequent menu changes or price alterations do not change historical order totals.
- **Implementation:** `OrderItem` table stores `item_name_snapshot` and `unit_price_snapshot`. Even if the restaurant updates item pricing tomorrow, previous order totals and receipts remain immutable.

### 3. Single Restaurant Order Integrity
- **Rule:** An order may contain items from exactly one restaurant.
- **Implementation:** `OrderService.create_order` inspects all referenced menu item IDs and verifies `item.restaurant_id == data.restaurant_id`. Rejects with `400 Bad Request` if items from multiple restaurants are mixed.

### 4. Ordering Availability & State Pre-conditions
- **Rule:** Orders cannot be placed for a closed restaurant (`is_open == False`) or for unavailable (`is_available == False`) or soft-deleted (`is_deleted == True`) items.
- **Implementation:** Pre-placement validation in `OrderService.create_order` checks `restaurant.is_open` and item availability flags before generating the order.

### 5. Configurable Tax & Delivery Charges
- **Rule:** Tax is a configurable percentage of item total (default 5%); delivery fee is free above a configurable order threshold (default 500, otherwise default 40).
- **Implementation:** Handled via Decimal arithmetic with 2 decimal precision in `app/utils/pricing.py`. Configuration values are loaded from environment variables (`TAX_PERCENTAGE`, `FREE_DELIVERY_THRESHOLD`, `DEFAULT_DELIVERY_FEE`).

### 6. Delivery Agent Action Authorization
- **Rule:** Only the assigned delivery agent may move an order to `PICKED_UP` or `DELIVERED`.
- **Implementation:** `DeliveryService.agent_update_delivery_status` enforces `order.agent_id == agent_id` and rejects any other agent with `403 Forbidden`.

### 7. Rating Eligibility & Singularity
- **Rule:** A rating can be submitted once, only by the ordering customer, and only for an order in `DELIVERED` status.
- **Implementation:** `RatingService.rate_order` enforces `order.customer_id == customer_id`, checks `order.status == OrderStatus.DELIVERED`, and enforces a unique constraint on `order_id` in `ratings`.

### 8. Dynamic Average Rating Recomputation
- **Rule:** The restaurant's average rating is automatically recomputed on every new rating.
- **Implementation:** `RatingRepository.get_restaurant_average_rating` performs an SQL `AVG()` aggregation across all ratings for that restaurant, and updates `restaurant.avg_rating` within the transaction.
