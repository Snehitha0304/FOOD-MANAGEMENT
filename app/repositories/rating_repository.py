from typing import Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.ratings import Rating
from app.models.orders import Order


class RatingRepository:
    def create(self, db: Session, rating: Rating) -> Rating:
        db.add(rating)
        db.commit()
        db.refresh(rating)
        return rating

    def get_by_order_id(self, db: Session, order_id: int) -> Optional[Rating]:
        stmt = select(Rating).where(Rating.order_id == order_id)
        return db.execute(stmt).scalars().first()

    def get_restaurant_average_rating(self, db: Session, restaurant_id: int) -> Decimal:
        stmt = (
            select(func.avg(Rating.restaurant_rating))
            .join(Order, Order.id == Rating.order_id)
            .where(Order.restaurant_id == restaurant_id)
        )
        avg_val = db.execute(stmt).scalar()
        if avg_val is not None:
            return Decimal(str(round(float(avg_val), 2)))
        return Decimal("0.00")

    def get_agent_average_rating(self, db: Session, agent_id: int) -> Optional[Decimal]:
        stmt = (
            select(func.avg(Rating.agent_rating))
            .join(Order, Order.id == Rating.order_id)
            .where(Order.agent_id == agent_id)
        )
        avg_val = db.execute(stmt).scalar()
        if avg_val is not None:
            return Decimal(str(round(float(avg_val), 2)))
        return None


rating_repository = RatingRepository()
