import sys
import os
from datetime import time, datetime, timedelta, timezone
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.core.constants import UserRole, OrderStatus
from app.models.users import User
from app.models.restaurants import Restaurant
from app.models.menu_categories import MenuCategory
from app.models.menu_items import MenuItem
from app.models.addresses import Address
from app.models.orders import Order
from app.models.order_items import OrderItem
from app.models.order_status_history import OrderStatusHistory
from app.models.ratings import Rating


def seed():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("🌱 Seeding database...")

        # 1. Check if already seeded
        existing_admin = db.query(User).filter(User.email == "admin@fooddelivery.com").first()
        if existing_admin:
            print("Base demo users already exist.")
            seed_orders(db)
            db.close()
            return

        # 2. Users
        admin = User(
            email="admin@fooddelivery.com",
            password_hash=get_password_hash("Admin@123"),
            full_name="Platform Admin",
            phone="+919876543210",
            role=UserRole.ADMIN,
            is_active=True
        )
        owner1 = User(
            email="owner1@fooddelivery.com",
            password_hash=get_password_hash("Owner@123"),
            full_name="Rajesh Sharma",
            phone="+919876543211",
            role=UserRole.RESTAURANT_OWNER,
            is_active=True
        )
        owner2 = User(
            email="owner2@fooddelivery.com",
            password_hash=get_password_hash("Owner@123"),
            full_name="Antonio Rossi",
            phone="+919876543212",
            role=UserRole.RESTAURANT_OWNER,
            is_active=True
        )
        agent1 = User(
            email="agent1@fooddelivery.com",
            password_hash=get_password_hash("Agent@123"),
            full_name="Suresh Kumar",
            phone="+919876543213",
            role=UserRole.DELIVERY_AGENT,
            is_active=True
        )
        agent2 = User(
            email="agent2@fooddelivery.com",
            password_hash=get_password_hash("Agent@123"),
            full_name="Ramesh Patel",
            phone="+919876543214",
            role=UserRole.DELIVERY_AGENT,
            is_active=True
        )
        customer1 = User(
            email="customer1@fooddelivery.com",
            password_hash=get_password_hash("Customer@123"),
            full_name="Aarav Verma",
            phone="+919876543215",
            role=UserRole.CUSTOMER,
            is_active=True
        )
        customer2 = User(
            email="customer2@fooddelivery.com",
            password_hash=get_password_hash("Customer@123"),
            full_name="Priya Nair",
            phone="+919876543216",
            role=UserRole.CUSTOMER,
            is_active=True
        )

        db.add_all([admin, owner1, owner2, agent1, agent2, customer1, customer2])
        db.commit()

        # 3. Restaurants
        rest1 = Restaurant(
            owner_id=owner1.id,
            name="Spice Junction",
            cuisine="North Indian",
            city="Bengaluru",
            address="12, 100 Feet Rd, Indiranagar",
            opens_at=time(9, 0),
            closes_at=time(23, 0),
            is_open=True,
            avg_rating=Decimal("0.00")
        )
        rest2 = Restaurant(
            owner_id=owner2.id,
            name="Pizza Roma",
            cuisine="Italian",
            city="Bengaluru",
            address="45, Koramangala 4th Block",
            opens_at=time(11, 0),
            closes_at=time(23, 0),
            is_open=True,
            avg_rating=Decimal("0.00")
        )
        db.add_all([rest1, rest2])
        db.commit()

        # 4. Menu Categories
        cat_starters = MenuCategory(restaurant_id=rest1.id, name="Starters", display_order=1)
        cat_mains = MenuCategory(restaurant_id=rest1.id, name="Main Course", display_order=2)
        cat_beverages = MenuCategory(restaurant_id=rest1.id, name="Beverages", display_order=3)
        cat_pizza = MenuCategory(restaurant_id=rest2.id, name="Artisan Pizzas", display_order=1)
        cat_pasta = MenuCategory(restaurant_id=rest2.id, name="Fresh Pastas", display_order=2)

        db.add_all([cat_starters, cat_mains, cat_beverages, cat_pizza, cat_pasta])
        db.commit()

        # 5. Menu Items
        items = [
            MenuItem(
                restaurant_id=rest1.id,
                category_id=cat_starters.id,
                name="Paneer Tikka",
                description="Chargrilled cottage cheese with aromatic spices",
                price=Decimal("220.00"),
                is_veg=True,
                is_available=True,
                is_deleted=False
            ),
            MenuItem(
                restaurant_id=rest1.id,
                category_id=cat_mains.id,
                name="Paneer Butter Masala",
                description="Rich cottage cheese curry with butter and cashews",
                price=Decimal("280.00"),
                is_veg=True,
                is_available=True,
                is_deleted=False
            ),
            MenuItem(
                restaurant_id=rest1.id,
                category_id=cat_mains.id,
                name="Butter Naan",
                description="Traditional clay oven flatbread layered with butter",
                price=Decimal("45.00"),
                is_veg=True,
                is_available=True,
                is_deleted=False
            ),
            MenuItem(
                restaurant_id=rest1.id,
                category_id=cat_mains.id,
                name="Hyderabadi Chicken Biryani",
                description="Fragrant basmati rice layered with spiced chicken",
                price=Decimal("340.00"),
                is_veg=False,
                is_available=True,
                is_deleted=False
            ),
            MenuItem(
                restaurant_id=rest1.id,
                category_id=cat_beverages.id,
                name="Sweet Mango Lassi",
                description="Chilled yogurt beverage made with Alphonso mangoes",
                price=Decimal("80.00"),
                is_veg=True,
                is_available=True,
                is_deleted=False
            ),
            MenuItem(
                restaurant_id=rest1.id,
                category_id=cat_starters.id,
                name="Seasonal Sweet Corn Chaat",
                description="Crispy corn tossed with chaat spices (Out of Stock)",
                price=Decimal("150.00"),
                is_veg=True,
                is_available=False,
                is_deleted=False
            ),
            MenuItem(
                restaurant_id=rest2.id,
                category_id=cat_pizza.id,
                name="Margherita Classica",
                description="San Marzano tomato sauce, fresh mozzarella, basil",
                price=Decimal("399.00"),
                is_veg=True,
                is_available=True,
                is_deleted=False
            ),
            MenuItem(
                restaurant_id=rest2.id,
                category_id=cat_pasta.id,
                name="Fettuccine Alfredo",
                description="Parmesan cream sauce with garlic and fresh herbs",
                price=Decimal("349.00"),
                is_veg=True,
                is_available=True,
                is_deleted=False
            ),
        ]
        db.add_all(items)
        db.commit()

        # 6. Customer Addresses
        addr1 = Address(
            user_id=customer1.id,
            line1="Flat 402, Green Heights",
            line2="100 Feet Road, Indiranagar",
            city="Bengaluru",
            pincode="560038",
            is_default=True
        )
        addr2 = Address(
            user_id=customer1.id,
            line1="Office Block B, Tech Park",
            line2="Outer Ring Road",
            city="Bengaluru",
            pincode="560103",
            is_default=False
        )
        addr3 = Address(
            user_id=customer2.id,
            line1="Villa 15, Palm Meadows",
            line2="Whitefield",
            city="Bengaluru",
            pincode="560066",
            is_default=True
        )
        db.add_all([addr1, addr2, addr3])
        db.commit()

        # 7-10. Orders, order items, status history, and ratings
        seed_orders(db)

        print("✅ Database successfully seeded!")
        print("Demo Users:")
        print("  - Admin: admin@fooddelivery.com / Admin@123")
        print("  - Owner 1: owner1@fooddelivery.com / Owner@123 (Spice Junction)")
        print("  - Owner 2: owner2@fooddelivery.com / Owner@123 (Pizza Roma)")
        print("  - Agent 1: agent1@fooddelivery.com / Agent@123")
        print("  - Agent 2: agent2@fooddelivery.com / Agent@123")
        print("  - Customer 1: customer1@fooddelivery.com / Customer@123")
        print("  - Customer 2: customer2@fooddelivery.com / Customer@123")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during seeding: {e}")
        raise e
    finally:
        db.close()


def seed_orders(db):
    """Seed demo orders and all order-related records if none exist."""
    if db.query(Order).count() > 0:
        print("Orders and related demo data already exist. Skipping.")
        return

    customer1 = db.query(User).filter(User.email == "customer1@fooddelivery.com").first()
    customer2 = db.query(User).filter(User.email == "customer2@fooddelivery.com").first()
    agent1 = db.query(User).filter(User.email == "agent1@fooddelivery.com").first()
    owner1 = db.query(User).filter(User.email == "owner1@fooddelivery.com").first()
    owner2 = db.query(User).filter(User.email == "owner2@fooddelivery.com").first()

    rest1 = db.query(Restaurant).filter(Restaurant.name == "Spice Junction").first()
    rest2 = db.query(Restaurant).filter(Restaurant.name == "Pizza Roma").first()

    addr1 = db.query(Address).filter(Address.user_id == customer1.id).filter(Address.is_default == True).first()
    addr2 = db.query(Address).filter(Address.user_id == customer2.id).filter(Address.is_default == True).first()

    if not all([customer1, customer2, agent1, owner1, owner2, rest1, rest2, addr1, addr2]):
        raise RuntimeError("Base seed data is incomplete. Run seed.py without existing demo data or restore the seed records.")

    paneer = db.query(MenuItem).filter(MenuItem.name == "Paneer Tikka").first()
    naan = db.query(MenuItem).filter(MenuItem.name == "Butter Naan").first()
    biryani = db.query(MenuItem).filter(MenuItem.name == "Hyderabadi Chicken Biryani").first()
    margherita = db.query(MenuItem).filter(MenuItem.name == "Margherita Classica").first()
    alfredo = db.query(MenuItem).filter(MenuItem.name == "Fettuccine Alfredo").first()

    if not all([paneer, naan, biryani, margherita, alfredo]):
        raise RuntimeError("Menu seed data is incomplete.")

    now = datetime.now(timezone.utc)

    order1 = Order(
        order_no="ORD-DEMO-DELIVERED-001",
        customer_id=customer1.id,
        restaurant_id=rest1.id,
        address_id=addr1.id,
        agent_id=agent1.id,
        status=OrderStatus.DELIVERED,
        item_total=Decimal("485.00"),
        tax_amount=Decimal("24.25"),
        delivery_fee=Decimal("40.00"),
        grand_total=Decimal("549.25"),
        placed_at=now - timedelta(days=2),
        delivered_at=now - timedelta(hours=30),
    )

    order2 = Order(
        order_no="ORD-DEMO-PREPARING-002",
        customer_id=customer2.id,
        restaurant_id=rest2.id,
        address_id=addr2.id,
        agent_id=agent1.id,
        status=OrderStatus.PREPARING,
        item_total=Decimal("748.00"),
        tax_amount=Decimal("37.40"),
        delivery_fee=Decimal("0.00"),
        grand_total=Decimal("785.40"),
        placed_at=now - timedelta(hours=3),
    )

    order3 = Order(
        order_no="ORD-DEMO-CANCELLED-003",
        customer_id=customer1.id,
        restaurant_id=rest1.id,
        address_id=addr1.id,
        agent_id=None,
        status=OrderStatus.CANCELLED,
        item_total=Decimal("420.00"),
        tax_amount=Decimal("21.00"),
        delivery_fee=Decimal("40.00"),
        grand_total=Decimal("481.00"),
        placed_at=now - timedelta(hours=8),
    )

    db.add_all([order1, order2, order3])
    db.flush()

    db.add_all([
        OrderItem(order_id=order1.id, menu_item_id=paneer.id, item_name_snapshot=paneer.name,
                  unit_price_snapshot=Decimal("220.00"), quantity=2, line_total=Decimal("440.00")),
        OrderItem(order_id=order1.id, menu_item_id=naan.id, item_name_snapshot=naan.name,
                  unit_price_snapshot=Decimal("45.00"), quantity=1, line_total=Decimal("45.00")),
        OrderItem(order_id=order2.id, menu_item_id=margherita.id, item_name_snapshot=margherita.name,
                  unit_price_snapshot=Decimal("399.00"), quantity=1, line_total=Decimal("399.00")),
        OrderItem(order_id=order2.id, menu_item_id=alfredo.id, item_name_snapshot=alfredo.name,
                  unit_price_snapshot=Decimal("349.00"), quantity=1, line_total=Decimal("349.00")),
        OrderItem(order_id=order3.id, menu_item_id=biryani.id, item_name_snapshot=biryani.name,
                  unit_price_snapshot=Decimal("340.00"), quantity=1, line_total=Decimal("340.00")),
    ])

    db.add_all([
        OrderStatusHistory(order_id=order1.id, from_status=None, to_status="PLACED",
                           changed_by=customer1.id, changed_at=now - timedelta(days=2), remark="Order placed"),
        OrderStatusHistory(order_id=order1.id, from_status="PLACED", to_status="CONFIRMED",
                           changed_by=owner1.id, changed_at=now - timedelta(days=2, hours=-1), remark="Restaurant confirmed"),
        OrderStatusHistory(order_id=order1.id, from_status="CONFIRMED", to_status="PREPARING",
                           changed_by=owner1.id, changed_at=now - timedelta(days=1, hours=20), remark="Preparation started"),
        OrderStatusHistory(order_id=order1.id, from_status="PREPARING", to_status="READY_FOR_PICKUP",
                           changed_by=owner1.id, changed_at=now - timedelta(days=1, hours=18), remark="Ready for pickup"),
        OrderStatusHistory(order_id=order1.id, from_status="READY_FOR_PICKUP", to_status="PICKED_UP",
                           changed_by=agent1.id, changed_at=now - timedelta(days=1, hours=14), remark="Picked up"),
        OrderStatusHistory(order_id=order1.id, from_status="PICKED_UP", to_status="DELIVERED",
                           changed_by=agent1.id, changed_at=now - timedelta(hours=30), remark="Delivered successfully"),

        OrderStatusHistory(order_id=order2.id, from_status=None, to_status="PLACED",
                           changed_by=customer2.id, changed_at=now - timedelta(hours=3), remark="Order placed"),
        OrderStatusHistory(order_id=order2.id, from_status="PLACED", to_status="CONFIRMED",
                           changed_by=owner2.id, changed_at=now - timedelta(hours=2, minutes=45), remark="Restaurant confirmed"),
        OrderStatusHistory(order_id=order2.id, from_status="CONFIRMED", to_status="PREPARING",
                           changed_by=owner2.id, changed_at=now - timedelta(hours=2, minutes=30), remark="Preparation started"),

        OrderStatusHistory(order_id=order3.id, from_status=None, to_status="PLACED",
                           changed_by=customer1.id, changed_at=now - timedelta(hours=8), remark="Order placed"),
        OrderStatusHistory(order_id=order3.id, from_status="PLACED", to_status="CANCELLED",
                           changed_by=customer1.id, changed_at=now - timedelta(hours=7), remark="Cancelled by customer"),
    ])

    db.add_all([
        Rating(order_id=order1.id, restaurant_rating=5, agent_rating=5,
               comment="Excellent food and very fast delivery."),
    ])

    db.commit()
    print("✅ Seeded orders, order items, status history, and ratings!")


if __name__ == "__main__":
    seed()
