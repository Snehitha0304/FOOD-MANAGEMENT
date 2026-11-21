from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.constants import OrderStatus
from app.models.base import TimestampMixin, utc_now


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="RESTRICT"), nullable=False, index=True)
    address_id = Column(Integer, ForeignKey("addresses.id", ondelete="RESTRICT"), nullable=False)
    agent_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PLACED, nullable=False, index=True)
    
    item_total = Column(Numeric(12, 2), nullable=False)
    tax_amount = Column(Numeric(12, 2), nullable=False)
    delivery_fee = Column(Numeric(12, 2), nullable=False)
    grand_total = Column(Numeric(12, 2), nullable=False)
    
    placed_at = Column(DateTime, default=utc_now, nullable=False)
    delivered_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("User", foreign_keys=[customer_id], back_populates="customer_orders")
    agent = relationship("User", foreign_keys=[agent_id], back_populates="assigned_orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    address = relationship("Address", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan", order_by="OrderStatusHistory.changed_at")
    rating = relationship("Rating", back_populates="order", uselist=False, cascade="all, delete-orphan")
