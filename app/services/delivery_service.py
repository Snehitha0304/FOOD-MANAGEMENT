import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.schemas.order import OrderResponse
from app.core.constants import OrderStatus, UserRole
from app.core.state_machine import validate_transition
from app.core.pagination import PageParams, PaginatedResponse
from app.repositories.order_repository import order_repository
from app.repositories.user_repository import user_repository
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    ForbiddenException,
    ConflictException
)

logger = logging.getLogger("audit")


class DeliveryService:
    def admin_assign_agent(self, db: Session, admin_id: int, order_id: int, agent_id: int) -> OrderResponse:
        order = order_repository.get_by_id(db, order_id)
        if not order:
            raise NotFoundException("Order not found", code="ORDER_NOT_FOUND")

        # Admin assigns agent when order is in READY_FOR_PICKUP (or CONFIRMED/PREPARING if admin wants to pre-assign)
        if order.status != OrderStatus.READY_FOR_PICKUP:
            raise ConflictException(
                f"Agent can only be assigned when order is in '{OrderStatus.READY_FOR_PICKUP.value}' state. Current state: '{order.status.value}'",
                code="INVALID_ORDER_STATE_FOR_ASSIGNMENT"
            )

        agent = user_repository.get_by_id(db, agent_id)
        if not agent or agent.role != UserRole.DELIVERY_AGENT:
            raise BadRequestException("Target user is not a valid delivery agent", code="INVALID_DELIVERY_AGENT")
        if not agent.is_active:
            raise BadRequestException("Delivery agent account is inactive", code="INACTIVE_DELIVERY_AGENT")

        updated_order = order_repository.assign_agent(db, order, agent_id, admin_id)
        logger.info(f"AUDIT: Admin {admin_id} assigned agent {agent_id} to order {order.id}")
        return OrderResponse.model_validate(updated_order)

    def get_agent_orders(
        self,
        db: Session,
        agent_id: int,
        status: Optional[OrderStatus] = None,
        params: Optional[PageParams] = None
    ) -> PaginatedResponse[OrderResponse]:
        if params is None:
            params = PageParams()

        orders, total = order_repository.get_by_agent_id(
            db=db,
            agent_id=agent_id,
            status=status,
            skip=params.offset,
            limit=params.size
        )
        items = [OrderResponse.model_validate(o) for o in orders]
        return PaginatedResponse.create(items, total, params)

    def agent_update_delivery_status(
        self,
        db: Session,
        agent_id: int,
        order_id: int,
        to_status: OrderStatus,
        remark: Optional[str] = None
    ) -> OrderResponse:
        order = order_repository.get_by_id(db, order_id)
        if not order:
            raise NotFoundException("Order not found", code="ORDER_NOT_FOUND")

        # Rule 6: Only the assigned agent may move an order to PICKED_UP / DELIVERED
        if order.agent_id != agent_id:
            raise ForbiddenException(
                "You are not the delivery agent assigned to this order",
                code="NOT_ASSIGNED_AGENT"
            )

        # Validate transition: READY_FOR_PICKUP -> PICKED_UP, PICKED_UP -> DELIVERED
        validate_transition(order.status, to_status, UserRole.DELIVERY_AGENT)

        updated_order = order_repository.record_transition(
            db=db,
            order=order,
            to_status=to_status,
            user_id=agent_id,
            remark=remark or f"Delivery status changed to {to_status.value} by delivery agent"
        )
        logger.info(f"AUDIT: Order {order.id} delivery status changed to {to_status.value} by agent {agent_id}")
        return OrderResponse.model_validate(updated_order)


delivery_service = DeliveryService()
