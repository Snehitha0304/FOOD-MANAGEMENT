# User Stories & Traceability Matrix

This document tracks all 24 User Stories from Case Study 04 and maps them directly to the implemented endpoints, services, and tests.

| # | Role | User Story | Implemented Endpoint | Service / Layer | Test Coverage |
|---|---|---|---|---|---|
| 1 | Visitor | Register as a customer so that I can place orders. | `POST /auth/register` | `AuthService.register_customer` | `tests/test_auth.py` |
| 2 | Admin | Onboard restaurant owner account to manage restaurant. | `POST /auth/admin/users` | `AuthService.admin_create_user` | `tests/test_auth.py` |
| 3 | Admin | Create delivery agent account so orders can be assigned. | `POST /auth/admin/users` | `AuthService.admin_create_user` | `tests/test_auth.py` |
| 4 | User | Log in and receive a JWT to call protected endpoints. | `POST /auth/login` | `AuthService.login` | `tests/test_auth.py`, `tests/security/test_jwt.py` |
| 5 | Restaurant Owner | Create and update restaurant profile with operating hours. | `POST /restaurants`<br>`PUT /restaurants/me` | `RestaurantService.create_restaurant`<br>`RestaurantService.update_my_restaurant` | `tests/test_restaurants.py` |
| 6 | Restaurant Owner | Mark restaurant open/closed to control ordering. | `PATCH /restaurants/me/open-status` | `RestaurantService.set_open_status` | `tests/test_restaurants.py`, `tests/test_orders.py` |
| 7 | Restaurant Owner | Manage menu categories to organize menu items. | `POST /restaurants/me/menu-categories`<br>`GET /restaurants/me/menu-categories`<br>`PUT /restaurants/me/menu-categories/{id}`<br>`DELETE /restaurants/me/menu-categories/{id}` | `MenuService.create_category`<br>`MenuService.update_category`<br>`MenuService.delete_category` | `tests/test_menu.py` |
| 8 | Restaurant Owner | Add, update and soft-delete menu items (price, veg flag). | `POST /restaurants/me/menu-items`<br>`PUT /menu-items/{id}`<br>`DELETE /menu-items/{id}` | `MenuService.create_menu_item`<br>`MenuService.update_menu_item`<br>`MenuService.soft_delete_menu_item` | `tests/test_menu.py`, `tests/ownership/test_owner_cannot_edit_other_menu.py` |
| 9 | Restaurant Owner | Toggle item availability for out-of-stock items. | `PATCH /menu-items/{id}/availability` | `MenuService.toggle_item_availability` | `tests/test_menu.py`, `tests/test_orders.py` |
| 10 | Customer | Search restaurants by name, cuisine, city with pagination. | `GET /restaurants?city=&cuisine=&name=&page=&size=` | `RestaurantService.search_restaurants` | `tests/test_restaurants.py` |
| 11 | Customer | View restaurant menu grouped by category. | `GET /restaurants/{id}/menu` | `MenuService.get_restaurant_menu_grouped` | `tests/test_menu.py` |
| 12 | Customer | Maintain multiple delivery addresses and mark one default. | `GET /addresses`<br>`POST /addresses`<br>`PUT /addresses/{id}/default`<br>`DELETE /addresses/{id}` | `CustomerService.get_addresses`<br>`CustomerService.create_address`<br>`CustomerService.set_default_address` | `tests/test_addresses.py`, `tests/test_customer.py` |
| 13 | Customer | View and update my own profile. | `GET /customer/profile`<br>`PUT /customer/profile` | `CustomerService.get_profile`<br>`CustomerService.update_profile` | `tests/test_addresses.py` |
| 14 | Customer | Place an order with multiple items and chosen address. | `POST /orders` | `OrderService.create_order` | `tests/test_orders.py` |
| 15 | Customer | System calculates item total, taxes, delivery fee, grand total. | `POST /orders` | `OrderService.create_order`, `pricing.py` | `tests/test_orders.py`, `tests/pricing/test_tampered_price.py` |
| 16 | Customer | Cancel order while still PLACED or CONFIRMED. | `PATCH /orders/{id}/cancel` | `OrderService.cancel_order` | `tests/test_orders.py`, `tests/state_machine/test_valid_transitions.py` |
| 17 | Customer | View my order history and detail of a single order. | `GET /orders/me`<br>`GET /orders/{id}` | `OrderService.get_customer_orders`<br>`OrderService.get_order_detail` | `tests/test_orders.py`, `tests/security/test_order_access.py` |
| 18 | Restaurant Owner | View incoming orders and accept (CONFIRMED) or reject. | `GET /orders/restaurant?status=`<br>`PATCH /orders/{id}/status` | `OrderService.restaurant_get_orders`<br>`OrderService.restaurant_update_status` | `tests/test_orders.py`, `tests/state_machine/test_valid_transitions.py` |
| 19 | Restaurant Owner | Mark order as PREPARING and READY_FOR_PICKUP. | `PATCH /orders/{id}/status` | `OrderService.restaurant_update_status` | `tests/test_delivery.py`, `tests/state_machine/test_valid_transitions.py` |
| 20 | Admin | Assign available delivery agent to READY_FOR_PICKUP order. | `PATCH /orders/{id}/assign-agent` | `DeliveryService.admin_assign_agent` | `tests/test_delivery.py` |
| 21 | Delivery Agent | View orders assigned to me. | `GET /orders/agent` | `DeliveryService.get_agent_orders` | `tests/test_delivery.py` |
| 22 | Delivery Agent | Mark order PICKED_UP and DELIVERED. | `PATCH /orders/{id}/delivery-status` | `DeliveryService.agent_update_delivery_status` | `tests/test_delivery.py` |
| 23 | Customer | Rate delivered order for restaurant and agent. | `POST /orders/{id}/rating` | `RatingService.rate_order` | `tests/test_ratings.py` |
| 24 | Customer | See restaurant average rating. | `GET /restaurants/{id}` | `RestaurantService.get_restaurant_by_id` | `tests/test_ratings.py`, `tests/test_restaurants.py` |
