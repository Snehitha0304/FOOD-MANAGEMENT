from sqlalchemy import Column, Integer, String, Boolean, Time, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Restaurant(Base, TimestampMixin):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False, index=True)
    cuisine = Column(String(100), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    address = Column(String(255), nullable=False)
    opens_at = Column(Time, nullable=False)
    closes_at = Column(Time, nullable=False)
    is_open = Column(Boolean, default=True, nullable=False)
    avg_rating = Column(Numeric(3, 2), default=0.00, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="restaurant")
    categories = relationship("MenuCategory", back_populates="restaurant", cascade="all, delete-orphan")
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="restaurant")
