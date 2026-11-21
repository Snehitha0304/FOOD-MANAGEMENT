from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.constants import OrderStatus
from app.dependencies.admin import get_current_admin
from app.dependencies.delivery_agent import get_current_agent
from app.models.users import User
from app.schemas.order import OrderAgentAssign, OrderDeliveryStatusUpdate, OrderResponse
from app.core.pagination import PageParams, PaginatedResponse
from app.services.delivery_service import delivery_service

router = APIRouter(tags=["Delivery"])


@router.patch(
    "/orders/{id}/assign-agent",
    response_model=OrderResponse,
    summary="Admin assign delivery agent to order (User Story 20)"
)
def assign_delivery_agent(
    id: int,
    data: OrderAgentAssign,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return delivery_service.admin_assign_agent(db, admin.id, id, data.agent_id)


@router.get(
    "/orders/agent",
    response_model=PaginatedResponse[OrderResponse],
    summary="Delivery agent view assigned orders (User Story 21)"
)
def get_agent_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    agent: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    params = PageParams(page=page, size=size)
    return delivery_service.get_agent_orders(db, agent.id, status=status, params=params)


@router.patch(
    "/orders/{id}/delivery-status",
    response_model=OrderResponse,
    summary="Delivery agent mark order PICKED_UP and DELIVERED (User Story 22)"
)
def update_delivery_status(
    id: int,
    data: OrderDeliveryStatusUpdate,
    agent: User = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    return delivery_service.agent_update_delivery_status(db, agent.id, id, data.status, data.remark)
