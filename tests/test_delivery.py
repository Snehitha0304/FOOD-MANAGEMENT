import pytest
from tests.conftest import auth_header


def test_delivery_lifecycle_and_phone_masking(client, seed_data):
    customer1 = seed_data["customer1"]
    owner1 = seed_data["owner1"]
    admin = seed_data["admin"]
    agent1 = seed_data["agent1"]
    rest1 = seed_data["restaurant1"]
    item1 = seed_data["item1"]
    addr1 = seed_data["address1"]

    # 1. Customer places order (PLACED)
    res = client.post(
        "/orders",
        headers=auth_header(customer1),
        json={
            "restaurant_id": rest1.id,
            "address_id": addr1.id,
            "items": [{"menu_item_id": item1.id, "quantity": 1}]
        }
    )
    assert res.status_code == 201
    order_id = res.json()["id"]

    # 2. Owner confirms and prepares order
    res_conf = client.patch(
        f"/orders/{order_id}/status",
        headers=auth_header(owner1),
        json={"status": "CONFIRMED"}
    )
    assert res_conf.status_code == 200

    res_prep = client.patch(
        f"/orders/{order_id}/status",
        headers=auth_header(owner1),
        json={"status": "PREPARING"}
    )
    assert res_prep.status_code == 200

    res_ready = client.patch(
        f"/orders/{order_id}/status",
        headers=auth_header(owner1),
        json={"status": "READY_FOR_PICKUP"}
    )
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "READY_FOR_PICKUP"

    # 3. Admin assigns delivery agent
    res_assign = client.patch(
        f"/orders/{order_id}/assign-agent",
        headers=auth_header(admin),
        json={"agent_id": agent1.id}
    )
    assert res_assign.status_code == 200
    assert res_assign.json()["agent_id"] == agent1.id

    # 4. Agent views assigned orders
    res_agent_orders = client.get("/orders/agent", headers=auth_header(agent1))
    assert res_agent_orders.status_code == 200
    assert any(o["id"] == order_id for o in res_agent_orders.json()["items"])

    # 5. Security Check: Customer phone number must be masked before PICKED_UP
    res_detail_before = client.get(f"/orders/{order_id}", headers=auth_header(agent1))
    assert res_detail_before.status_code == 200
    assert res_detail_before.json()["customer_phone"] is None

    # 6. Agent marks PICKED_UP
    res_pickup = client.patch(
        f"/orders/{order_id}/delivery-status",
        headers=auth_header(agent1),
        json={"status": "PICKED_UP"}
    )
    assert res_pickup.status_code == 200
    assert res_pickup.json()["status"] == "PICKED_UP"

    # 7. Security Check: Customer phone number is now exposed after PICKED_UP!
    res_detail_after = client.get(f"/orders/{order_id}", headers=auth_header(agent1))
    assert res_detail_after.status_code == 200
    assert res_detail_after.json()["customer_phone"] == customer1.phone

    # 8. Agent marks DELIVERED
    res_delivered = client.patch(
        f"/orders/{order_id}/delivery-status",
        headers=auth_header(agent1),
        json={"status": "DELIVERED"}
    )
    assert res_delivered.status_code == 200
    assert res_delivered.json()["status"] == "DELIVERED"
    assert res_delivered.json()["delivered_at"] is not None
