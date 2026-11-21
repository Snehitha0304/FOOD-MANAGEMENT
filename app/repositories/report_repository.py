from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func, case
from app.models.orders import Order
from app.models.ratings import Rating
from app.models.users import User
from app.core.constants import OrderStatus, UserRole


class ReportRepository:
    def get_restaurant_sales(
        self,
        db: Session,
        restaurant_id: Optional[int] = None
    ) -> Dict[str, Any]:
        delivered_revenue = case((Order.status == OrderStatus.DELIVERED, Order.grand_total), else_=0)
        delivered_count = case((Order.status == OrderStatus.DELIVERED, 1), else_=0)
        cancelled_count = case((Order.status.in_([OrderStatus.CANCELLED, OrderStatus.REJECTED]), 1), else_=0)

        stmt = select(
            func.count(Order.id).label("total_orders"),
            func.coalesce(func.sum(delivered_revenue), 0).label("total_revenue"),
            func.coalesce(func.sum(delivered_count), 0).label("completed_orders"),
            func.coalesce(func.sum(cancelled_count), 0).label("cancelled_orders")
        )
        if restaurant_id:
            stmt = stmt.where(Order.restaurant_id == restaurant_id)

        row = db.execute(stmt).first()
        total_orders = row.total_orders or 0
        total_revenue = Decimal(str(row.total_revenue or 0.00))
        completed_orders = row.completed_orders or 0
        cancelled_orders = row.cancelled_orders or 0
        
        avg_order_value = (
            Decimal(str(round(float(total_revenue) / completed_orders, 2)))
            if completed_orders > 0 else Decimal("0.00")
        )

        return {
            "restaurant_id": restaurant_id,
            "total_orders": total_orders,
            "completed_orders": completed_orders,
            "cancelled_orders": cancelled_orders,
            "total_revenue": total_revenue,
            "avg_order_value": avg_order_value
        }

    def get_agent_performance(self, db: Session) -> List[Dict[str, Any]]:
        agents_stmt = select(User).where(User.role == UserRole.DELIVERY_AGENT)
        agents = list(db.execute(agents_stmt).scalars().all())

        results = []
        for agent in agents:
            assigned_count = db.execute(
                select(func.count(Order.id)).where(Order.agent_id == agent.id)
            ).scalar() or 0
            
            delivered_count = db.execute(
                select(func.count(Order.id)).where(Order.agent_id == agent.id, Order.status == OrderStatus.DELIVERED)
            ).scalar() or 0

            avg_rating = db.execute(
                select(func.avg(Rating.agent_rating))
                .join(Order, Order.id == Rating.order_id)
                .where(Order.agent_id == agent.id)
            ).scalar()
            
            avg_rating_decimal = Decimal(str(round(float(avg_rating), 2))) if avg_rating is not None else None

            results.append({
                "agent_id": agent.id,
                "agent_name": agent.full_name,
                "total_assigned": assigned_count,
                "total_delivered": delivered_count,
                "avg_rating": avg_rating_decimal
            })
        return results

    def get_cancellation_rate(self, db: Session) -> Dict[str, Any]:
        total_orders = db.execute(select(func.count(Order.id))).scalar() or 0
        cancelled_orders = db.execute(
            select(func.count(Order.id)).where(Order.status == OrderStatus.CANCELLED)
        ).scalar() or 0
        rejected_orders = db.execute(
            select(func.count(Order.id)).where(Order.status == OrderStatus.REJECTED)
        ).scalar() or 0

        rate = (
            Decimal(str(round(((cancelled_orders + rejected_orders) / total_orders) * 100, 2)))
            if total_orders > 0 else Decimal("0.00")
        )

        return {
            "total_orders": total_orders,
            "cancelled_orders": cancelled_orders,
            "rejected_orders": rejected_orders,
            "cancellation_rate_percentage": rate
        }


report_repository = ReportRepository()
