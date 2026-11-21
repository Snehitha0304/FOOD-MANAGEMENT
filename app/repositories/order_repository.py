from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.orders import Order
from app.models.order_items import OrderItem
from app.models.order_status_history import OrderStatusHistory
from app.core.constants import OrderStatus


class OrderRepository:
    def create(self, db: Session, order: Order, items: List[OrderItem], user_id: int) -> Order:
        db.add(order)
        db.flush()  # populate order.id
        
        for item in items:
            item.order_id = order.id
            db.add(item)
            
        initial_history = OrderStatusHistory(
            order_id=order.id,
            from_status=None,
            to_status=OrderStatus.PLACED.value,
            changed_by=user_id,
            changed_at=datetime.now(timezone.utc),
            remark="Order placed successfully"
        )
        db.add(initial_history)
        
        db.commit()
        db.refresh(order)
        return order

    def get_by_id(self, db: Session, order_id: int) -> Optional[Order]:
        return db.get(Order, order_id)

    def get_by_order_no(self, db: Session, order_no: str) -> Optional[Order]:
        stmt = select(Order).where(Order.order_no == order_no)
        return db.execute(stmt).scalars().first()

    def get_by_customer_id(
        self,
        db: Session,
        customer_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> Tuple[List[Order], int]:
        count_stmt = select(func.count(Order.id)).where(Order.customer_id == customer_id)
        stmt = (
            select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.placed_at.desc())
            .offset(skip)
            .limit(limit)
        )
        total = db.execute(count_stmt).scalar() or 0
        items = list(db.execute(stmt).scalars().all())
        return items, total

    def get_by_restaurant_id(
        self,
        db: Session,
        restaurant_id: int,
        status: Optional[OrderStatus] = None,
        skip: int = 0,
        limit: int = 10
    ) -> Tuple[List[Order], int]:
        stmt = select(Order).where(Order.restaurant_id == restaurant_id)
        count_stmt = select(func.count(Order.id)).where(Order.restaurant_id == restaurant_id)

        if status:
            stmt = stmt.where(Order.status == status)
            count_stmt = count_stmt.where(Order.status == status)

        total = db.execute(count_stmt).scalar() or 0
        items = list(db.execute(stmt.order_by(Order.placed_at.desc()).offset(skip).limit(limit)).scalars().all())
        return items, total

    def get_by_agent_id(
        self,
        db: Session,
        agent_id: int,
        status: Optional[OrderStatus] = None,
        skip: int = 0,
        limit: int = 10
    ) -> Tuple[List[Order], int]:
        stmt = select(Order).where(Order.agent_id == agent_id)
        count_stmt = select(func.count(Order.id)).where(Order.agent_id == agent_id)

        if status:
            stmt = stmt.where(Order.status == status)
            count_stmt = count_stmt.where(Order.status == status)

        total = db.execute(count_stmt).scalar() or 0
        items = list(db.execute(stmt.order_by(Order.placed_at.desc()).offset(skip).limit(limit)).scalars().all())
        return items, total

    def record_transition(
        self,
        db: Session,
        order: Order,
        to_status: OrderStatus,
        user_id: int,
        remark: Optional[str] = None
    ) -> Order:
        from_status = order.status.value if hasattr(order.status, "value") else str(order.status)
        order.status = to_status
        now_utc = datetime.now(timezone.utc)
        
        if to_status == OrderStatus.DELIVERED:
            order.delivered_at = now_utc
            
        history = OrderStatusHistory(
            order_id=order.id,
            from_status=from_status,
            to_status=to_status.value,
            changed_by=user_id,
            changed_at=now_utc,
            remark=remark
        )
        db.add(history)
        db.commit()
        db.refresh(order)
        return order

    def assign_agent(self, db: Session, order: Order, agent_id: int, user_id: int) -> Order:
        order.agent_id = agent_id
        history = OrderStatusHistory(
            order_id=order.id,
            from_status=order.status.value,
            to_status=order.status.value,
            changed_by=user_id,
            changed_at=datetime.now(timezone.utc),
            remark=f"Delivery agent assigned: ID {agent_id}"
        )
        db.add(history)
        db.commit()
        db.refresh(order)
        return order


order_repository = OrderRepository()
