from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.constants import UserRole
from app.models.base import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="owner", uselist=False, cascade="all, delete-orphan")
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    customer_orders = relationship("Order", foreign_keys="[Order.customer_id]", back_populates="customer")
    assigned_orders = relationship("Order", foreign_keys="[Order.agent_id]", back_populates="agent")
    status_changes = relationship("OrderStatusHistory", back_populates="user")
