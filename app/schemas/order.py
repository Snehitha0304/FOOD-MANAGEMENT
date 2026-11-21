from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field
from app.core.constants import OrderStatus


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = Field(..., ge=1)
    price: Optional[Decimal] = Field(None, description="Client-supplied price, ignored by server")


class OrderCreate(BaseModel):
    restaurant_id: int
    address_id: int
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    remark: Optional[str] = None


class OrderAgentAssign(BaseModel):
    agent_id: int


class OrderDeliveryStatusUpdate(BaseModel):
    status: OrderStatus
    remark: Optional[str] = None


class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    item_name_snapshot: str
    unit_price_snapshot: Decimal
    quantity: int
    line_total: Decimal

    class Config:
        from_attributes = True


class OrderStatusHistoryResponse(BaseModel):
    id: int
    order_id: int
    from_status: Optional[str]
    to_status: str
    changed_by: int
    changed_at: datetime
    remark: Optional[str]

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    order_no: str
    customer_id: int
    restaurant_id: int
    address_id: int
    agent_id: Optional[int]
    status: OrderStatus
    item_total: Decimal
    tax_amount: Decimal
    delivery_fee: Decimal
    grand_total: Decimal
    placed_at: datetime
    delivered_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderDetailResponse(OrderResponse):
    customer_phone: Optional[str] = None
    customer_name: Optional[str] = None
    items: List[OrderItemResponse] = []
    status_history: List[OrderStatusHistoryResponse] = []
