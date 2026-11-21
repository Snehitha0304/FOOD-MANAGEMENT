from app.core.constants import UserRole, OrderStatus
from app.core.exceptions import ForbiddenException, NotFoundException


def check_restaurant_ownership(restaurant, user_id: int):
    if not restaurant:
        raise NotFoundException("Restaurant not found", code="RESTAURANT_NOT_FOUND")
    if restaurant.owner_id != user_id:
        raise ForbiddenException(
            detail="You do not have permission to manage this restaurant",
            code="NOT_RESTAURANT_OWNER"
        )


def check_order_access(order, current_user):
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    user_id = current_user.id
    
    if user_role == UserRole.ADMIN.value:
        return
    
    if user_role == UserRole.CUSTOMER.value and order.customer_id == user_id:
        return
        
    if user_role == UserRole.RESTAURANT_OWNER.value and order.restaurant.owner_id == user_id:
        return
        
    if user_role == UserRole.DELIVERY_AGENT.value and order.agent_id == user_id:
        return
        
    raise ForbiddenException(
        detail="You do not have permission to access this order",
        code="ORDER_ACCESS_FORBIDDEN"
    )
