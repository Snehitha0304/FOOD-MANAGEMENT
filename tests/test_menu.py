import pytest
from decimal import Decimal
from tests.conftest import auth_header


def test_manage_categories(client, seed_data):
    owner1 = seed_data["owner1"]
    # 1. Create category
    res = client.post(
        "/restaurants/me/menu-categories",
        headers=auth_header(owner1),
        json={"name": "Desserts", "display_order": 5}
    )
    assert res.status_code == 201
    cat_id = res.json()["id"]

    # 2. List categories
    res_list = client.get(
        "/restaurants/me/menu-categories",
        headers=auth_header(owner1)
    )
    assert res_list.status_code == 200
    assert any(c["id"] == cat_id for c in res_list.json())

    # 3. Update category
    res_up = client.put(
        f"/restaurants/me/menu-categories/{cat_id}",
        headers=auth_header(owner1),
        json={"name": "Exotic Desserts"}
    )
    assert res_up.status_code == 200
    assert res_up.json()["name"] == "Exotic Desserts"


def test_create_and_update_menu_item(client, seed_data):
    owner1 = seed_data["owner1"]
    cat1 = seed_data["category1"]

    # Create item
    res = client.post(
        "/restaurants/me/menu-items",
        headers=auth_header(owner1),
        json={
            "category_id": cat1.id,
            "name": "Chicken Tikka",
            "description": "Tender grilled chicken",
            "price": "290.00",
            "is_veg": False,
            "is_available": True
        }
    )
    assert res.status_code == 201
    item_id = res.json()["id"]
    assert res.json()["name"] == "Chicken Tikka"

    # Update item
    res_up = client.put(
        f"/menu-items/{item_id}",
        headers=auth_header(owner1),
        json={"price": "310.00"}
    )
    assert res_up.status_code == 200
    assert Decimal(str(res_up.json()["price"])) == Decimal("310.00")


def test_toggle_item_availability(client, seed_data):
    owner1 = seed_data["owner1"]
    item1 = seed_data["item1"]

    res = client.patch(
        f"/menu-items/{item1.id}/availability",
        headers=auth_header(owner1),
        json={"is_available": False}
    )
    assert res.status_code == 200
    assert res.json()["is_available"] is False


def test_soft_delete_menu_item(client, seed_data):
    owner1 = seed_data["owner1"]
    item1 = seed_data["item1"]

    res = client.delete(
        f"/menu-items/{item1.id}",
        headers=auth_header(owner1)
    )
    assert res.status_code == 200
    assert res.json()["is_deleted"] is True
    assert res.json()["is_available"] is False


def test_view_grouped_menu(client, seed_data):
    rest1 = seed_data["restaurant1"]
    res = client.get(f"/restaurants/{rest1.id}/menu")
    assert res.status_code == 200
    data = res.json()
    assert data["restaurant_id"] == rest1.id
    assert len(data["categories"]) >= 1
    assert any(len(c["items"]) > 0 for c in data["categories"])
