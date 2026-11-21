import pytest
from tests.conftest import auth_header


def test_create_restaurant_success(client, db_session):
    from app.core.security import get_password_hash
    from app.core.constants import UserRole
    from app.models.users import User

    new_owner = User(
        email="unassigned_owner@test.com",
        password_hash=get_password_hash("Owner@123"),
        full_name="Unassigned Owner",
        phone="+919999990000",
        role=UserRole.RESTAURANT_OWNER,
        is_active=True
    )
    db_session.add(new_owner)
    db_session.commit()

    response = client.post(
        "/restaurants",
        headers=auth_header(new_owner),
        json={
            "name": "Bites & Bowls",
            "cuisine": "Continental",
            "city": "Bengaluru",
            "address": "Brigade Road",
            "opens_at": "08:00:00",
            "closes_at": "22:00:00",
            "is_open": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Bites & Bowls"
    assert data["owner_id"] == new_owner.id


def test_create_duplicate_restaurant_for_owner(client, seed_data):
    owner1 = seed_data["owner1"]
    response = client.post(
        "/restaurants",
        headers=auth_header(owner1),
        json={
            "name": "Second Restaurant",
            "cuisine": "Fast Food",
            "city": "Bengaluru",
            "address": "MG Road",
            "opens_at": "10:00:00",
            "closes_at": "22:00:00",
            "is_open": True
        }
    )
    assert response.status_code == 409


def test_update_my_restaurant(client, seed_data):
    owner1 = seed_data["owner1"]
    response = client.put(
        "/restaurants/me",
        headers=auth_header(owner1),
        json={
            "name": "Royal Spice Grand",
            "cuisine": "North Indian & Mughlai"
        }
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Royal Spice Grand"


def test_toggle_restaurant_open_status(client, seed_data):
    owner1 = seed_data["owner1"]
    response = client.patch(
        "/restaurants/me/open-status",
        headers=auth_header(owner1),
        json={"is_open": False}
    )
    assert response.status_code == 200
    assert response.json()["is_open"] is False


def test_search_restaurants_with_pagination_and_filters(client, seed_data):
    # Filter by cuisine
    res1 = client.get("/restaurants?cuisine=Indian&page=1&size=5")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["total"] >= 1
    assert any(r["name"] == "Royal Spice" for r in data1["items"])

    # Filter by city
    res2 = client.get("/restaurants?city=Bengaluru&page=1&size=10")
    assert res2.status_code == 200
    assert res2.json()["total"] >= 2


def test_get_restaurant_by_id(client, seed_data):
    rest1 = seed_data["restaurant1"]
    res = client.get(f"/restaurants/{rest1.id}")
    assert res.status_code == 200
    assert res.json()["name"] == "Royal Spice"
