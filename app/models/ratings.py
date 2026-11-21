from sqlalchemy import Column, Integer, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Rating(Base, TimestampMixin):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    restaurant_rating = Column(Integer, nullable=False)
    agent_rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint("restaurant_rating >= 1 AND restaurant_rating <= 5", name="check_restaurant_rating_range"),
        CheckConstraint("agent_rating >= 1 AND agent_rating <= 5", name="check_agent_rating_range"),
    )

    # Relationships
    order = relationship("Order", back_populates="rating")
