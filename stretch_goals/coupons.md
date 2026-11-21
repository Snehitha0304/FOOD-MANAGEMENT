# Stretch Goal: Coupon Codes Architecture & Design

## Objective
Support dynamic promotional discount codes providing either percentage-based discounts (e.g. 20% off up to ₹100) or flat-amount discounts (e.g. ₹50 off), bounded by validity date windows, minimum order values, and usage caps.

## Database Schema Extension

```sql
CREATE TABLE coupons (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_type VARCHAR(20) NOT NULL, -- 'PERCENTAGE' or 'FLAT'
    discount_value NUMERIC(12, 2) NOT NULL,
    max_discount_amount NUMERIC(12, 2) NULL, -- Cap for percentage discounts
    min_order_value NUMERIC(12, 2) DEFAULT 0.00 NOT NULL,
    valid_from TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_until TIMESTAMP WITH TIME ZONE NOT NULL,
    usage_limit_per_user INT DEFAULT 1 NOT NULL,
    total_usage_limit INT NULL,
    times_used INT DEFAULT 0 NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE coupon_usages (
    id SERIAL PRIMARY KEY,
    coupon_id INT REFERENCES coupons(id),
    user_id INT REFERENCES users(id),
    order_id INT REFERENCES orders(id),
    discount_applied NUMERIC(12, 2) NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

## Calculation Logic in Order Pricing
1. Customer supplies `coupon_code` during checkout in `OrderCreate`.
2. `OrderService` verifies:
   - Coupon exists and `is_active == True`.
   - `valid_from <= current_utc_time <= valid_until`.
   - `item_total >= coupon.min_order_value`.
   - User's usage count for this coupon < `usage_limit_per_user`.
   - Total coupon usages < `total_usage_limit`.
3. Computation:
   - For `PERCENTAGE`: `discount = min((item_total * discount_value / 100), max_discount_amount)`.
   - For `FLAT`: `discount = min(discount_value, item_total)`.
4. `grand_total = item_total - discount + tax_amount + delivery_fee`.
5. Atomic row insertion into `coupon_usages` on order confirmation.
