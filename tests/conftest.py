import functools
import pytest
from datetime import time
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.core.constants import UserRole
from app.models.users import User
from app.models.restaurants import Restaurant
from app.models.menu_categories import MenuCategory
from app.models.menu_items import MenuItem
from app.models.addresses import Address
from app.main import app

@functools.lru_cache(maxsize=32)
def get_cached_password_hash(pwd: str) -> str:
    return get_password_hash(pwd)

# In-memory SQLite database for high-speed, isolated unit tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seed_data(db_session):
    # Admin
    admin = User(
        email="admin@test.com",
        password_hash=get_cached_password_hash("Admin@123"),
        full_name="Admin User",
        phone="+919999999990",
        role=UserRole.ADMIN,
        is_active=True
    )
    # Owner 1
    owner1 = User(
        email="owner1@test.com",
        password_hash=get_cached_password_hash("Owner@123"),
        full_name="Owner One",
        phone="+919999999991",
        role=UserRole.RESTAURANT_OWNER,
        is_active=True
    )
    # Owner 2
    owner2 = User(
        email="owner2@test.com",
        password_hash=get_cached_password_hash("Owner@123"),
        full_name="Owner Two",
        phone="+919999999992",
        role=UserRole.RESTAURANT_OWNER,
        is_active=True
    )
    # Agent 1
    agent1 = User(
        email="agent1@test.com",
        password_hash=get_cached_password_hash("Agent@123"),
        full_name="Agent One",
        phone="+919999999993",
        role=UserRole.DELIVERY_AGENT,
        is_active=True
    )
    # Customer 1
    customer1 = User(
        email="customer1@test.com",
        password_hash=get_cached_password_hash("Customer@123"),
        full_name="Customer One",
        phone="+919999999994",
        role=UserRole.CUSTOMER,
        is_active=True
    )
    # Customer 2
    customer2 = User(
        email="customer2@test.com",
        password_hash=get_cached_password_hash("Customer@123"),
        full_name="Customer Two",
        phone="+919999999995",
        role=UserRole.CUSTOMER,
        is_active=True
    )

    db_session.add_all([admin, owner1, owner2, agent1, customer1, customer2])
    db_session.commit()

    # Restaurant 1 (Owner 1)
    rest1 = Restaurant(
        owner_id=owner1.id,
        name="Royal Spice",
        cuisine="Indian",
        city="Bengaluru",
        address="100 Feet Rd",
        opens_at=time(9, 0),
        closes_at=time(23, 0),
        is_open=True,
        avg_rating=Decimal("0.00")
    )
    # Restaurant 2 (Owner 2)
    rest2 = Restaurant(
        owner_id=owner2.id,
        name="Napoli Bites",
        cuisine="Italian",
        city="Bengaluru",
        address="Indiranagar",
        opens_at=time(11, 0),
        closes_at=time(22, 0),
        is_open=True,
        avg_rating=Decimal("0.00")
    )
    db_session.add_all([rest1, rest2])
    db_session.commit()

    # Category & Item for Rest 1
    cat1 = MenuCategory(restaurant_id=rest1.id, name="Curries", display_order=1)
    db_session.add(cat1)
    db_session.commit()

    item1 = MenuItem(
        restaurant_id=rest1.id,
        category_id=cat1.id,
        name="Paneer Tikka Masala",
        description="Spicy cottage cheese",
        price=Decimal("250.00"),
        is_veg=True,
        is_available=True,
        is_deleted=False
    )
    item2 = MenuItem(
        restaurant_id=rest1.id,
        category_id=cat1.id,
        name="Garlic Naan",
        description="Clay oven bread",
        price=Decimal("50.00"),
        is_veg=True,
        is_available=True,
        is_deleted=False
    )
    item_unavailable = MenuItem(
        restaurant_id=rest1.id,
        category_id=cat1.id,
        name="Out of Stock Sweet",
        description="Unavailable",
        price=Decimal("100.00"),
        is_veg=True,
        is_available=False,
        is_deleted=False
    )
    db_session.add_all([item1, item2, item_unavailable])
    db_session.commit()

    # Address for Customer 1
    addr1 = Address(
        user_id=customer1.id,
        line1="123 Main St",
        line2="Apt 4B",
        city="Bengaluru",
        pincode="560001",
        is_default=True
    )
    db_session.add(addr1)
    db_session.commit()

    return {
        "admin": admin,
        "owner1": owner1,
        "owner2": owner2,
        "agent1": agent1,
        "customer1": customer1,
        "customer2": customer2,
        "restaurant1": rest1,
        "restaurant2": rest2,
        "category1": cat1,
        "item1": item1,
        "item2": item2,
        "item_unavailable": item_unavailable,
        "address1": addr1
    }


def auth_header(user: User) -> dict:
    token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value, "email": user.email}
    )
    return {"Authorization": f"Bearer {token}"}
