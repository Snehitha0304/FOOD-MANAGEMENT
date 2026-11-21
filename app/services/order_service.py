import logging
from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.orders import Order
from app.models.order_items import OrderItem
from app.models.users import User
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderDetailResponse,
    OrderItemResponse,
    OrderStatusHistoryResponse
)
from app.core.constants import OrderStatus, UserRole
from app.core.state_machine import validate_transition
from app.core.pagination import PageParams, PaginatedResponse
from app.repositories.order_repository import order_repository
from app.repositories.restaurant_repository import restaurant_repository
from app.repositories.menu_repository import menu_repository
from app.repositories.address_repository import address_repository
from app.utils.pricing import calculate_order_totals, round_currency
from app.utils.order_number import generate_order_number
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    ForbiddenException,
    ConflictException
)

logger = logging.getLogger("audit")


class OrderService:
    def create_order(self, db: Session, customer_id: int, data: OrderCreate) -> OrderResponse:
        # 1. Verify restaurant exists and is open
        restaurant = restaurant_repository.get_by_id(db, data.restaurant_id)
        if not restaurant:
            raise NotFoundException("Restaurant not found", code="RESTAURANT_NOT_FOUND")
        if not restaurant.is_open:
            raise BadRequestException("Cannot place order: Restaurant is currently closed", code="RESTAURANT_CLOSED")

        # 2. Verify address exists and belongs to customer
        address = address_repository.get_by_id(db, data.address_id)
        if not address or address.user_id != customer_id:
            raise BadRequestException("Invalid delivery address", code="INVALID_ADDRESS")

        # 3. Retrieve menu items and validate
        item_ids = [item_in.menu_item_id for item_in in data.items]
        db_items = menu_repository.get_items_by_ids(db, item_ids)
        db_items_map = {item.id: item for item in db_items}

        if len(db_items_map) != len(set(item_ids)):
            raise BadRequestException("One or more menu items do not exist", code="INVALID_MENU_ITEM")

        order_items: List[OrderItem] = []
        pricing_inputs = []

        for item_in in data.items:
            db_item = db_items_map[item_in.menu_item_id]

            # Rule 3: Single restaurant check
            if db_item.restaurant_id != data.restaurant_id:
                raise BadRequestException(
                    "All items in an order must be from the same restaurant",
                    code="MULTIPLE_RESTAURANTS_NOT_ALLOWED"
                )

            # Rule 4: Availability and deleted checks
            if db_item.is_deleted or not db_item.is_available:
                raise BadRequestException(
                    f"Item '{db_item.name}' is currently unavailable or has been removed",
                    code="ITEM_UNAVAILABLE"
                )

            # Rule 1 & 2: Server-side pricing snapshotting (ignore any client-supplied price)
            unit_price = round_currency(Decimal(str(db_item.price)))
            line_total = round_currency(unit_price * Decimal(item_in.quantity))
            
            pricing_inputs.append((unit_price, item_in.quantity))

            order_items.append(
                OrderItem(
                    menu_item_id=db_item.id,
                    item_name_snapshot=db_item.name,
                    unit_price_snapshot=unit_price,
                    quantity=item_in.quantity,
                    line_total=line_total
                )
            )

        # Rule 5: Calculate totals
        item_total, tax_amount, delivery_fee, grand_total = calculate_order_totals(pricing_inputs)

        order = Order(
            order_no=generate_order_number(),
            customer_id=customer_id,
            restaurant_id=data.restaurant_id,
            address_id=data.address_id,
            status=OrderStatus.PLACED,
            item_total=item_total,
            tax_amount=tax_amount,
            delivery_fee=delivery_fee,
            grand_total=grand_total
        )

        created_order = order_repository.create(db, order, order_items, customer_id)
        logger.info(f"AUDIT: Order '{created_order.order_no}' created by customer {customer_id} for grand total {grand_total}")
        return OrderResponse.model_validate(created_order)

    def cancel_order(self, db: Session, customer_id: int, order_id: int) -> OrderResponse:
        order = order_repository.get_by_id(db, order_id)
        if not order:
            raise NotFoundException("Order not found", code="ORDER_NOT_FOUND")
        if order.customer_id != customer_id:
            raise ForbiddenException("You can only cancel your own orders", code="ORDER_OWNERSHIP_VIOLATION")

        # Validate state machine transition for Customer
        validate_transition(order.status, OrderStatus.CANCELLED, UserRole.CUSTOMER)

        updated_order = order_repository.record_transition(
            db=db,
            order=order,
            to_status=OrderStatus.CANCELLED,
            user_id=customer_id,
            remark="Order cancelled by customer"
        )
        logger.info(f"AUDIT: Order {order.id} cancelled by customer {customer_id}")
        return OrderResponse.model_validate(updated_order)

    def get_customer_orders(
        self,
        db: Session,
        customer_id: int,
        params: Optional[PageParams] = None
    ) -> PaginatedResponse[OrderResponse]:
        if params is None:
            params = PageParams()
        orders, total = order_repository.get_by_customer_id(db, customer_id, skip=params.offset, limit=params.size)
        items = [OrderResponse.model_validate(o) for o in orders]
        return PaginatedResponse.create(items, total, params)

    def get_order_detail(self, db: Session, current_user: User, order_id: int) -> OrderDetailResponse:
        order = order_repository.get_by_id(db, order_id)
        if not order:
            raise NotFoundException("Order not found", code="ORDER_NOT_FOUND")

        # Role & Ownership checks (Participant-only access)
        user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
        is_admin = user_role == UserRole.ADMIN.value
        is_customer = user_role == UserRole.CUSTOMER.value and order.customer_id == current_user.id
        is_owner = user_role == UserRole.RESTAURANT_OWNER.value and order.restaurant.owner_id == current_user.id
        is_agent = user_role == UserRole.DELIVERY_AGENT.value and order.agent_id == current_user.id

        if not (is_admin or is_customer or is_owner or is_agent):
            raise ForbiddenException("You do not have access to view this order", code="ORDER_ACCESS_FORBIDDEN")

        order_dict = OrderResponse.model_validate(order).model_dump()
        items = [OrderItemResponse.model_validate(item) for item in order.items]
        status_history = [OrderStatusHistoryResponse.model_validate(h) for h in order.status_history]

        order_dict["items"] = items
        order_dict["status_history"] = status_history
        order_dict["customer_name"] = order.customer.full_name

        # Security requirement: Customer phone numbers must be exposed to delivery agent ONLY after PICKED_UP
        if is_agent and order.status not in [OrderStatus.PICKED_UP, OrderStatus.DELIVERED]:
            order_dict["customer_phone"] = None
        else:
            order_dict["customer_phone"] = order.customer.phone

        return OrderDetailResponse(**order_dict)

    def restaurant_get_orders(
        self,
        db: Session,
        owner_id: int,
        status: Optional[OrderStatus] = None,
        params: Optional[PageParams] = None
    ) -> PaginatedResponse[OrderResponse]:
        restaurant = restaurant_repository.get_by_owner_id(db, owner_id)
        if not restaurant:
            raise ForbiddenException("You do not have a registered restaurant", code="RESTAURANT_NOT_FOUND")

        if params is None:
            params = PageParams()

        orders, total = order_repository.get_by_restaurant_id(
            db=db,
            restaurant_id=restaurant.id,
            status=status,
            skip=params.offset,
            limit=params.size
        )
        items = [OrderResponse.model_validate(o) for o in orders]
        return PaginatedResponse.create(items, total, params)

    def restaurant_update_status(
        self,
        db: Session,
        owner_id: int,
        order_id: int,
        to_status: OrderStatus,
        remark: Optional[str] = None
    ) -> OrderResponse:
        restaurant = restaurant_repository.get_by_owner_id(db, owner_id)
        if not restaurant:
            raise ForbiddenException("You do not have a registered restaurant", code="RESTAURANT_NOT_FOUND")

        order = order_repository.get_by_id(db, order_id)
        if not order:
            raise NotFoundException("Order not found", code="ORDER_NOT_FOUND")
        if order.restaurant_id != restaurant.id:
            raise ForbiddenException("Order does not belong to your restaurant", code="ORDER_OWNERSHIP_VIOLATION")

        # Validate transition
        validate_transition(order.status, to_status, UserRole.RESTAURANT_OWNER)

        updated_order = order_repository.record_transition(
            db=db,
            order=order,
            to_status=to_status,
            user_id=owner_id,
            remark=remark or f"Status changed to {to_status.value} by restaurant owner"
        )
        logger.info(f"AUDIT: Order {order.id} transitioned to {to_status.value} by restaurant owner {owner_id}")
        return OrderResponse.model_validate(updated_order)


order_service = OrderService()
