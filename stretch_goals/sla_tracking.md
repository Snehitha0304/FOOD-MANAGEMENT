# Stretch Goal: Order-Level SLA Tracking

## Objective
Monitor and flag delivery orders that risk breaching service-level agreements (SLAs), allowing proactive kitchen escalations and agent interventions.

## SLA Targets & Thresholds
- **Kitchen Preparation SLA ($T_{prep}$):** Max 20 minutes from `CONFIRMED` to `READY_FOR_PICKUP`.
- **Pickup SLA ($T_{pickup}$):** Max 10 minutes from `READY_FOR_PICKUP` to `PICKED_UP`.
- **Total Delivery SLA ($T_{delivery}$):** Max 45 minutes from `PLACED` to `DELIVERED`.

## Implementation Strategy

### 1. Database Schema Extension
Add SLA deadline columns to `orders`:
```sql
ALTER TABLE orders ADD COLUMN expected_delivery_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE orders ADD COLUMN is_sla_breached BOOLEAN DEFAULT FALSE NOT NULL;
ALTER TABLE orders ADD COLUMN sla_breach_reason VARCHAR(255) NULL;
```

### 2. Live Calculation & Flagging Endpoint
`GET /reports/sla-breaches` (Admin only)
```python
def check_sla_breaches(db: Session, max_minutes: int = 45):
    threshold_time = datetime.now(timezone.utc) - timedelta(minutes=max_minutes)
    breached_orders = (
        db.query(Order)
        .filter(Order.status.in_([OrderStatus.PLACED, OrderStatus.CONFIRMED, OrderStatus.PREPARING, OrderStatus.READY_FOR_PICKUP, OrderStatus.PICKED_UP]))
        .filter(Order.placed_at < threshold_time)
        .all()
    )
    return [
        {
            "order_id": o.id,
            "order_no": o.order_no,
            "current_status": o.status.value,
            "elapsed_minutes": int((datetime.now(timezone.utc) - o.placed_at).total_seconds() / 60),
            "restaurant_id": o.restaurant_id,
            "agent_id": o.agent_id
        }
        for o in breached_orders
    ]
```

### 3. Background Celery / Cron Poller
A periodic task runs every 2 minutes checking for orders nearing SLA breach, alerting dispatchers and restaurant managers via webhooks.
