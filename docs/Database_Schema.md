# Database Schema & Data Dictionary

The relational schema is built and managed via Alembic migrations.

## Tables & Columns

### 1. `users`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto | Unique User Identifier |
| `email` | String(255) | Unique, Index, Not Null | User login email |
| `password_hash` | String(255) | Not Null | Bcrypt hashed password |
| `full_name` | String(100) | Not Null | User's full name |
| `phone` | String(20) | Not Null | Contact phone number |
| `role` | String(50) | Not Null | Enum: ADMIN, RESTAURANT_OWNER, CUSTOMER, DELIVERY_AGENT |
| `is_active` | Boolean | Default True, Not Null | Active status flag |
| `created_at` | DateTime (UTC) | Not Null | Row creation timestamp |
| `updated_at` | DateTime (UTC) | Not Null | Row update timestamp |

### 2. `restaurants`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto | Restaurant Identifier |
| `owner_id` | Integer | FK users.id, Unique, Index, Not Null | Owner User ID (1-to-1) |
| `name` | String(150) | Index, Not Null | Restaurant name |
| `cuisine` | String(100) | Index, Not Null | Cuisine type (e.g. North Indian, Italian) |
| `city` | String(100) | Index, Not Null | City (e.g. Bengaluru) |
| `address` | String(255) | Not Null | Physical street address |
| `opens_at` | Time | Not Null | Daily opening time |
| `closes_at` | Time | Not Null | Daily closing time |
| `is_open` | Boolean | Default True, Not Null | Operational open/closed toggle |
| `avg_rating` | Numeric(3, 2) | Default 0.00, Not Null | Recomputed average rating |
| `created_at` | DateTime (UTC) | Not Null | Timestamp |
| `updated_at` | DateTime (UTC) | Not Null | Timestamp |

### 3. `menu_categories`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto | Category Identifier |
| `restaurant_id` | Integer | FK restaurants.id, Index, Not Null | Associated restaurant |
| `name` | String(100) | Not Null | Category name |
| `display_order` | Integer | Default 0, Not Null | Sort order in menu view |
| `created_at` | DateTime (UTC) | Not Null | Timestamp |
| `updated_at` | DateTime (UTC) | Not Null | Timestamp |

### 4. `menu_items`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto | Item Identifier |
| `restaurant_id` | Integer | FK restaurants.id, Index, Not Null | Associated restaurant |
| `category_id` | Integer | FK menu_categories.id, Index, Not Null | Menu category |
| `name` | String(150) | Index, Not Null | Dish name |
| `description` | Text | Nullable | Dish details |
| `price` | Numeric(12, 2) | Not Null | Base catalog price |
| `is_veg` | Boolean | Default True, Not Null | Vegetarian indicator |
| `is_available` | Boolean | Default True, Not Null | Stock availability toggle |
| `is_deleted` | Boolean | Default False, Not Null | Soft delete indicator |
| `created_at` | DateTime (UTC) | Not Null | Timestamp |
| `updated_at` | DateTime (UTC) | Not Null | Timestamp |

### 5. `addresses`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto | Address Identifier |
| `user_id` | Integer | FK users.id, Index, Not Null | Customer user ID |
| `line1` | String(255) | Not Null | House/Street |
| `line2` | String(255) | Nullable | Area/Landmark |
| `city` | String(100) | Index, Not Null | City name |
| `pincode` | String(10) | Not Null | Postal PIN code |
| `is_default` | Boolean | Default False, Not Null | Default address flag |
| `created_at` | DateTime (UTC) | Not Null | Timestamp |
| `updated_at` | DateTime (UTC) | Not Null | Timestamp |

### 6. `orders`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto | Order internal ID |
| `order_no` | String(50) | Unique, Index, Not Null | Human-readable order number (ORD-YYYYMMDD-XXXX) |
| `customer_id` | Integer | FK users.id, Index, Not Null | Customer user ID |
| `restaurant_id` | Integer | FK restaurants.id, Index, Not Null | Restaurant ID |
| `address_id` | Integer | FK addresses.id, Not Null | Delivery address |
| `agent_id` | Integer | FK users.id, Index, Nullable | Assigned delivery agent |
| `status` | String(50) | Index, Not Null | OrderStatus Enum |
| `item_total` | Numeric(12, 2) | Not Null | Computed sum of line items |
| `tax_amount` | Numeric(12, 2) | Not Null | Computed tax (5%) |
| `delivery_fee` | Numeric(12, 2) | Not Null | Delivery fee |
| `grand_total` | Numeric(12, 2) | Not Null | Total payable amount |
| `placed_at` | DateTime (UTC) | Not Null | Placement timestamp |
| `delivered_at` | DateTime (UTC) | Nullable | Delivery completion timestamp |
| `created_at` | DateTime (UTC) | Not Null | Timestamp |
| `updated_at` | DateTime (UTC) | Not Null | Timestamp |

### 7. `order_items`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto | Line item ID |
| `order_id` | Integer | FK orders.id, Index, Not Null | Associated order |
| `menu_item_id` | Integer | FK menu_items.id, Not Null | Original menu item ID |
| `item_name_snapshot` | String(150) | Not Null | Snapshotted name at order time |
| `unit_price_snapshot` | Numeric(12, 2) | Not Null | Snapshotted unit price at order time |
| `quantity` | Integer | Not Null | Quantity ordered |
| `line_total` | Numeric(12, 2) | Not Null | Snapshotted unit_price * quantity |
| `created_at` | DateTime (UTC) | Not Null | Timestamp |
| `updated_at` | DateTime (UTC) | Not Null | Timestamp |

### 8. `order_status_history`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto | History record ID |
| `order_id` | Integer | FK orders.id, Index, Not Null | Associated order |
| `from_status` | String(50) | Nullable | Previous status |
| `to_status` | String(50) | Not Null | New status |
| `changed_by` | Integer | FK users.id, Not Null | User ID who made the change |
| `changed_at` | DateTime (UTC) | Not Null | Transition timestamp |
| `remark` | Text | Nullable | Optional note or audit log |

### 9. `ratings`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, Auto | Rating ID |
| `order_id` | Integer | FK orders.id, Unique, Index, Not Null | Single rating per order |
| `restaurant_rating` | Integer | Check (1-5), Not Null | Score for food quality (1-5) |
| `agent_rating` | Integer | Check (1-5), Not Null | Score for delivery agent (1-5) |
| `comment` | Text | Nullable | Customer feedback |
| `created_at` | DateTime (UTC) | Not Null | Timestamp |
| `updated_at` | DateTime (UTC) | Not Null | Timestamp |
