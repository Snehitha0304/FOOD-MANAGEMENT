import sys
import os
from datetime import time
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.core.constants import UserRole
from app.models.users import User
from app.models.restaurants import Restaurant
from app.models.menu_categories import MenuCategory
from app.models.menu_items import MenuItem
from app.models.addresses import Address


def seed():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("🌱 Seeding database...")

        # 1. Check if already seeded
        existing_admin = db.query(User).filter(User.email == "admin@fooddelivery.com").first()
        if existing_admin:
            print("Database already contains seed data. Skipping.")
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


if __name__ == "__main__":
    seed()
