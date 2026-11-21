from typing import Dict, List, Tuple
from app.core.constants import OrderStatus, UserRole
from app.core.exceptions import ConflictException, ForbiddenException

# Valid transitions: from_status -> list of valid to_status
VALID_TRANSITIONS: Dict[OrderStatus, List[OrderStatus]] = {
    OrderStatus.PLACED: [OrderStatus.CONFIRMED, OrderStatus.REJECTED, OrderStatus.CANCELLED],
    OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
    OrderStatus.PREPARING: [OrderStatus.READY_FOR_PICKUP],
    OrderStatus.READY_FOR_PICKUP: [OrderStatus.PICKED_UP],
    OrderStatus.PICKED_UP: [OrderStatus.DELIVERED],
    OrderStatus.REJECTED: [],
    OrderStatus.CANCELLED: [],
    OrderStatus.DELIVERED: []
}

# Role permissions for specific transitions: (from_status, to_status) -> allowed UserRole(s)
TRANSITION_ROLES: Dict[Tuple[OrderStatus, OrderStatus], List[UserRole]] = {
    (OrderStatus.PLACED, OrderStatus.CONFIRMED): [UserRole.RESTAURANT_OWNER],
    (OrderStatus.PLACED, OrderStatus.REJECTED): [UserRole.RESTAURANT_OWNER],
    (OrderStatus.PLACED, OrderStatus.CANCELLED): [UserRole.CUSTOMER],
    (OrderStatus.CONFIRMED, OrderStatus.PREPARING): [UserRole.RESTAURANT_OWNER],
    (OrderStatus.CONFIRMED, OrderStatus.CANCELLED): [UserRole.CUSTOMER],
    (OrderStatus.PREPARING, OrderStatus.READY_FOR_PICKUP): [UserRole.RESTAURANT_OWNER],
    (OrderStatus.READY_FOR_PICKUP, OrderStatus.PICKED_UP): [UserRole.DELIVERY_AGENT],
    (OrderStatus.PICKED_UP, OrderStatus.DELIVERED): [UserRole.DELIVERY_AGENT],
}


def validate_transition(
    current_status: OrderStatus,
    target_status: OrderStatus,
    user_role: UserRole
) -> None:
    # 1. State machine check
    valid_targets = VALID_TRANSITIONS.get(current_status, [])
    if target_status not in valid_targets:
        raise ConflictException(
            detail=f"Invalid state transition from '{current_status.value}' to '{target_status.value}'.",
            code="INVALID_STATUS_TRANSITION"
        )
    
    # 2. Role permission check (Admins can perform any valid transition if necessary, but specific roles are enforced)
    if user_role != UserRole.ADMIN:
        allowed_roles = TRANSITION_ROLES.get((current_status, target_status), [])
        if user_role not in allowed_roles:
            raise ForbiddenException(
                detail=f"Role '{user_role.value}' is not authorized to transition order from '{current_status.value}' to '{target_status.value}'.",
                code="ROLE_NOT_AUTHORIZED_FOR_TRANSITION"
            )
