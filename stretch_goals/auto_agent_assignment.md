# Stretch Goal: Automatic Delivery Agent Assignment

## Objective
Automatically match and assign the most suitable, available delivery agent to an order as soon as it transitions into `READY_FOR_PICKUP`, optimizing for minimal active delivery load and geographical proximity.

## Assignment Strategy: Fewest Active Deliveries (Load Balancing)

### Algorithm
1. Triggered automatically on order transition:
   When `OrderService.restaurant_update_status` moves an order to `READY_FOR_PICKUP`.
2. Query active agents:
   Fetch all delivery agents (`role == DELIVERY_AGENT`, `is_active == True`).
3. Calculate active load:
   Count orders in statuses `[READY_FOR_PICKUP, PICKED_UP]` for each agent.
   ```sql
   SELECT u.id, u.full_name, COUNT(o.id) AS active_orders
   FROM users u
   LEFT JOIN orders o ON o.agent_id = u.id AND o.status IN ('READY_FOR_PICKUP', 'PICKED_UP')
   WHERE u.role = 'DELIVERY_AGENT' AND u.is_active = TRUE
   GROUP BY u.id
   ORDER BY active_orders ASC, RANDOM()
   LIMIT 1;
   ```
4. If eligible agent found:
   - Assign `order.agent_id = selected_agent.id`.
   - Insert `order_status_history` record with remark: `"Auto-assigned delivery agent ID <id> based on load balancing"`.
   - Dispatch real-time notification (push/websocket/SMS) to the assigned agent.
5. Fallback:
   If no agents are active or within delivery threshold, flag order for manual Admin assignment.
