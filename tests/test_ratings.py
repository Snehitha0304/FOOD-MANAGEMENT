import pytest
from decimal import Decimal
from tests.conftest import auth_header


def test_order_rating_lifecycle(client, seed_data):
    customer1 = seed_data["customer1"]
    customer2 = seed_data["customer2"]
    owner1 = seed_data["owner1"]
    admin = seed_data["admin"]
    agent1 = seed_data["agent1"]
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

    # Try rating before DELIVERED -> 400
    res_early_rating = client.post(
        f"/orders/{order_id}/rating",
        headers=auth_header(customer1),
        json={"restaurant_rating": 5, "agent_rating": 5, "comment": "Too fast"}
    )
    assert res_early_rating.status_code == 400

    # Move order to DELIVERED
    client.patch(f"/orders/{order_id}/status", headers=auth_header(owner1), json={"status": "CONFIRMED"})
    client.patch(f"/orders/{order_id}/status", headers=auth_header(owner1), json={"status": "PREPARING"})
    client.patch(f"/orders/{order_id}/status", headers=auth_header(owner1), json={"status": "READY_FOR_PICKUP"})
    client.patch(f"/orders/{order_id}/assign-agent", headers=auth_header(admin), json={"agent_id": agent1.id})
    client.patch(f"/orders/{order_id}/delivery-status", headers=auth_header(agent1), json={"status": "PICKED_UP"})
    client.patch(f"/orders/{order_id}/delivery-status", headers=auth_header(agent1), json={"status": "DELIVERED"})

    # Try rating by different customer -> 403
    res_other = client.post(
        f"/orders/{order_id}/rating",
        headers=auth_header(customer2),
        json={"restaurant_rating": 4, "agent_rating": 4}
    )
    assert res_other.status_code == 403

    # Successful rating by ordering customer
    res_rate = client.post(
        f"/orders/{order_id}/rating",
        headers=auth_header(customer1),
        json={"restaurant_rating": 5, "agent_rating": 4, "comment": "Delicious food and prompt delivery!"}
    )
    assert res_rate.status_code == 201
    assert res_rate.json()["restaurant_rating"] == 5
    assert res_rate.json()["agent_rating"] == 4

    # Verify restaurant average rating is updated
    res_rest = client.get(f"/restaurants/{rest1.id}")
    assert res_rest.status_code == 200
    assert Decimal(str(res_rest.json()["avg_rating"])) == Decimal("5.00")

    # Second rating attempt on same order -> 409
    res_duplicate = client.post(
        f"/orders/{order_id}/rating",
        headers=auth_header(customer1),
        json={"restaurant_rating": 5, "agent_rating": 5}
    )
    assert res_duplicate.status_code == 409
