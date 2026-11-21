import pytest
from decimal import Decimal
from tests.conftest import auth_header


def test_place_order_and_calculate_pricing(client, seed_data):
    customer1 = seed_data["customer1"]
    rest1 = seed_data["restaurant1"]
    item1 = seed_data["item1"]  # 250.00
    item2 = seed_data["item2"]  # 50.00
    addr1 = seed_data["address1"]

    # Order item1 x 1 (250) + item2 x 2 (100) = 350 item total
    # Tax = 5% of 350 = 17.50
    # Delivery fee: 350 < 500 => 40.00
    # Grand total = 350 + 17.50 + 40.00 = 407.50
    res = client.post(
        "/orders",
        headers=auth_header(customer1),
        json={
            "restaurant_id": rest1.id,
            "address_id": addr1.id,
            "items": [
                {"menu_item_id": item1.id, "quantity": 1},
                {"menu_item_id": item2.id, "quantity": 2}
            ]
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert Decimal(str(data["item_total"])) == Decimal("350.00")
    assert Decimal(str(data["tax_amount"])) == Decimal("17.50")
    assert Decimal(str(data["delivery_fee"])) == Decimal("40.00")
    assert Decimal(str(data["grand_total"])) == Decimal("407.50")
    assert data["status"] == "PLACED"
    assert "order_no" in data


def test_free_delivery_above_threshold(client, seed_data):
    customer1 = seed_data["customer1"]
    rest1 = seed_data["restaurant1"]
    item1 = seed_data["item1"]  # 250.00
    addr1 = seed_data["address1"]

    # Order item1 x 3 = 750 (>= 500 threshold -> free delivery)
    # Tax = 5% of 750 = 37.50
    # Delivery fee = 0.00
    # Grand total = 750 + 37.50 = 787.50
    res = client.post(
        "/orders",
        headers=auth_header(customer1),
        json={
            "restaurant_id": rest1.id,
            "address_id": addr1.id,
            "items": [
                {"menu_item_id": item1.id, "quantity": 3}
            ]
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert Decimal(str(data["item_total"])) == Decimal("750.00")
    assert Decimal(str(data["delivery_fee"])) == Decimal("0.00")
    assert Decimal(str(data["grand_total"])) == Decimal("787.50")


def test_cannot_order_from_closed_restaurant(client, seed_data):
    customer1 = seed_data["customer1"]
    rest1 = seed_data["restaurant1"]
    owner1 = seed_data["owner1"]
    item1 = seed_data["item1"]
    addr1 = seed_data["address1"]

    # Close restaurant
    client.patch("/restaurants/me/open-status", headers=auth_header(owner1), json={"is_open": False})

    res = client.post(
        "/orders",
        headers=auth_header(customer1),
        json={
            "restaurant_id": rest1.id,
            "address_id": addr1.id,
            "items": [{"menu_item_id": item1.id, "quantity": 1}]
        }
    )
    assert res.status_code == 400
    assert res.json()["code"] == "RESTAURANT_CLOSED"


def test_cannot_order_unavailable_item(client, seed_data):
    customer1 = seed_data["customer1"]
    rest1 = seed_data["restaurant1"]
    item_un = seed_data["item_unavailable"]
    addr1 = seed_data["address1"]

    res = client.post(
        "/orders",
        headers=auth_header(customer1),
        json={
            "restaurant_id": rest1.id,
            "address_id": addr1.id,
            "items": [{"menu_item_id": item_un.id, "quantity": 1}]
        }
    )
    assert res.status_code == 400
    assert res.json()["code"] == "ITEM_UNAVAILABLE"


def test_cannot_order_items_from_multiple_restaurants(client, seed_data, db_session):
    customer1 = seed_data["customer1"]
    rest1 = seed_data["restaurant1"]
    rest2 = seed_data["restaurant2"]
    item1 = seed_data["item1"]  # Rest 1
    addr1 = seed_data["address1"]

    from app.models.menu_categories import MenuCategory
    from app.models.menu_items import MenuItem

    cat2 = MenuCategory(restaurant_id=rest2.id, name="Italian", display_order=1)
    db_session.add(cat2)
    db_session.commit()
    item_rest2 = MenuItem(
        restaurant_id=rest2.id,
        category_id=cat2.id,
        name="Pasta",
        price=Decimal("200.00"),
        is_veg=True,
        is_available=True,
        is_deleted=False
    )
    db_session.add(item_rest2)
    db_session.commit()

    res = client.post(
        "/orders",
        headers=auth_header(customer1),
        json={
            "restaurant_id": rest1.id,
            "address_id": addr1.id,
            "items": [
                {"menu_item_id": item1.id, "quantity": 1},
                {"menu_item_id": item_rest2.id, "quantity": 1}
            ]
        }
    )
    assert res.status_code == 400
    assert res.json()["code"] == "MULTIPLE_RESTAURANTS_NOT_ALLOWED"


def test_customer_cancel_order(client, seed_data):
    customer1 = seed_data["customer1"]
    rest1 = seed_data["restaurant1"]
    item1 = seed_data["item1"]
    addr1 = seed_data["address1"]

    # Place order
    res = client.post(
        "/orders",
        headers=auth_header(customer1),
        json={
            "restaurant_id": rest1.id,
            "address_id": addr1.id,
            "items": [{"menu_item_id": item1.id, "quantity": 1}]
        }
    )
    order_id = res.json()["id"]

    # Cancel order
    res_cancel = client.patch(f"/orders/{order_id}/cancel", headers=auth_header(customer1))
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "CANCELLED"
