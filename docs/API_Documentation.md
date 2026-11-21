# API Documentation & Surface Reference

The API is fully documented via interactive OpenAPI (Swagger UI) at `http://127.0.0.1:8000/docs` and ReDoc at `http://127.0.0.1:8000/redoc`.

All endpoints are available both directly at the root paths and prefixed under `/api/v1`.

## Endpoints Summary

### Authentication Module
- `POST /auth/register` — Public. Register as a customer. Returns 201 Created.
- `POST /auth/login` — Public. OAuth2 password flow or JSON body login. Returns access token, user ID, role.
- `POST /auth/admin/users` — Role: `ADMIN`. Onboard Restaurant Owners or Delivery Agents.

### Restaurant Module
- `POST /restaurants` — Role: `RESTAURANT_OWNER`. Create restaurant profile with opening/closing hours.
- `GET /restaurants/me` — Role: `RESTAURANT_OWNER`. View own restaurant profile.
- `PUT /restaurants/me` — Role: `RESTAURANT_OWNER`. Update own restaurant profile.
- `PATCH /restaurants/me/open-status` — Role: `RESTAURANT_OWNER`. Toggle open/closed status.
- `GET /restaurants` — Public. Search restaurants with filters (`city`, `cuisine`, `name`) and pagination (`page`, `size`).
- `GET /restaurants/{id}` — Public. View restaurant detail including recomputed average rating.
- `GET /restaurants/{id}/menu` — Public. View restaurant menu grouped by category.

### Menu Module
- `POST /restaurants/me/menu-categories` — Role: `RESTAURANT_OWNER`. Create a category.
- `GET /restaurants/me/menu-categories` — Role: `RESTAURANT_OWNER`. List categories.
- `PUT /restaurants/me/menu-categories/{id}` — Role: `RESTAURANT_OWNER`. Update a category.
- `DELETE /restaurants/me/menu-categories/{id}` — Role: `RESTAURANT_OWNER`. Delete a category.
- `POST /restaurants/me/menu-items` — Role: `RESTAURANT_OWNER`. Add menu item with price and veg flag.
- `PUT /menu-items/{id}` — Role: `RESTAURANT_OWNER`. Update menu item.
- `DELETE /menu-items/{id}` — Role: `RESTAURANT_OWNER`. Soft-delete menu item (`is_deleted=True`).
- `PATCH /menu-items/{id}/availability` — Role: `RESTAURANT_OWNER`. Toggle item stock availability.

### Customer Module
- `GET /customer/profile` — Role: `CUSTOMER`. View profile.
- `PUT /customer/profile` — Role: `CUSTOMER`. Update profile.
- `GET /addresses` — Role: `CUSTOMER`. List saved delivery addresses.
- `POST /addresses` — Role: `CUSTOMER`. Add new delivery address.
- `PUT /addresses/{id}/default` — Role: `CUSTOMER`. Mark address as default.
- `DELETE /addresses/{id}` — Role: `CUSTOMER`. Remove delivery address.

### Order Module
- `POST /orders` — Role: `CUSTOMER`. Place an order. Pricing calculated server-side; client price ignored.
- `GET /orders/me` — Role: `CUSTOMER`. View order history with pagination.
- `GET /orders/{id}` — Roles: Participant only (`CUSTOMER` owner, `RESTAURANT_OWNER`, assigned `DELIVERY_AGENT`, `ADMIN`). Phone masked before `PICKED_UP`.
- `PATCH /orders/{id}/cancel` — Role: `CUSTOMER`. Cancel order while `PLACED` or `CONFIRMED`.
- `GET /orders/restaurant` — Role: `RESTAURANT_OWNER`. View incoming orders with optional status filter.
- `PATCH /orders/{id}/status` — Role: `RESTAURANT_OWNER`. Accept (`CONFIRMED`), reject (`REJECTED`), prepare (`PREPARING`), or ready (`READY_FOR_PICKUP`).

### Delivery Module
- `PATCH /orders/{id}/assign-agent` — Role: `ADMIN`. Assign agent to `READY_FOR_PICKUP` order.
- `GET /orders/agent` — Role: `DELIVERY_AGENT`. View assigned orders.
- `PATCH /orders/{id}/delivery-status` — Role: `DELIVERY_AGENT`. Move order to `PICKED_UP` or `DELIVERED`.

### Rating Module
- `POST /orders/{id}/rating` — Role: `CUSTOMER`. Rate delivered order (1-5 stars for restaurant and agent).

### Reporting Module
- `GET /reports/restaurant-sales` — Roles: `RESTAURANT_OWNER`, `ADMIN`. Sales metrics, order counts, revenue.
- `GET /reports/agent-performance` — Role: `ADMIN`. Delivery agent completion stats and average ratings.
- `GET /reports/cancellation-rate` — Role: `ADMIN`. Platform cancellation and rejection rate analytics.

### Health Module
- `GET /health` — Public. Returns service status, database connectivity, and timestamp.
