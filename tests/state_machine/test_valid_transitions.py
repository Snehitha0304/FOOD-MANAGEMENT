import pytest
from tests.conftest import auth_header


def test_full_valid_state_machine_and_audit_history(client, seed_data):
    customer1 = seed_data["customer1"]
    owner1 = seed_data["owner1"]
    admin = seed_data["admin"]
    agent1 = seed_data["agent1"]
    rest1 = seed_data["restaurant1"]
    item1 = seed_data["item1"]
    addr1 = seed_data["address1"]

    # 1. PLACED
    res1 = client.post(
        "/orders",
        headers=auth_header(customer1),
        json={
            "restaurant_id": rest1.id,
            "address_id": addr1.id,
            "items": [{"menu_item_id": item1.id, "quantity": 1}]
        }
    )
    assert res1.status_code == 201
    order_id = res1.json()["id"]

    # 2. CONFIRMED
    res2 = client.patch(
        f"/orders/{order_id}/status",
        headers=auth_header(owner1),
        json={"status": "CONFIRMED", "remark": "Accepted by kitchen"}
    )
    assert res2.status_code == 200
    assert res2.json()["status"] == "CONFIRMED"

    # 3. PREPARING
    res3 = client.patch(
        f"/orders/{order_id}/status",
        headers=auth_header(owner1),
        json={"status": "PREPARING", "remark": "Cooking started"}
    )
    assert res3.status_code == 200
    assert res3.json()["status"] == "PREPARING"

    # 4. READY_FOR_PICKUP
    res4 = client.patch(
        f"/orders/{order_id}/status",
        headers=auth_header(owner1),
        json={"status": "READY_FOR_PICKUP", "remark": "Packed and ready"}
    )
    assert res4.status_code == 200
    assert res4.json()["status"] == "READY_FOR_PICKUP"

    # 5. ADMIN ASSIGN AGENT
    res_assign = client.patch(
        f"/orders/{order_id}/assign-agent",
        headers=auth_header(admin),
        json={"agent_id": agent1.id}
    )
    assert res_assign.status_code == 200
    assert res_assign.json()["agent_id"] == agent1.id

    # 6. PICKED_UP
    res5 = client.patch(
        f"/orders/{order_id}/delivery-status",
        headers=auth_header(agent1),
        json={"status": "PICKED_UP", "remark": "Agent picked up the package"}
    )
    assert res5.status_code == 200
    assert res5.json()["status"] == "PICKED_UP"

    # 7. DELIVERED
    res6 = client.patch(
        f"/orders/{order_id}/delivery-status",
        headers=auth_header(agent1),
        json={"status": "DELIVERED", "remark": "Delivered to customer doorstep"}
    )
    assert res6.status_code == 200
    assert res6.json()["status"] == "DELIVERED"
    assert res6.json()["delivered_at"] is not None

    # Verify Order Status History contains every step
    detail = client.get(f"/orders/{order_id}", headers=auth_header(admin)).json()
    history = detail["status_history"]
    assert len(history) >= 6
    history_statuses = [h["to_status"] for h in history]
    assert "PLACED" in history_statuses
    assert "CONFIRMED" in history_statuses
    assert "PREPARING" in history_statuses
    assert "READY_FOR_PICKUP" in history_statuses
    assert "PICKED_UP" in history_statuses
    assert "DELIVERED" in history_statuses


def test_placed_to_rejected_transition(client, seed_data):
    customer1 = seed_data["customer1"]
    owner1 = seed_data["owner1"]
    rest1 = seed_data["restaurant1"]
    item1 = seed_data["item1"]
    addr1 = seed_data["address1"]

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

    res_rej = client.patch(
        f"/orders/{order_id}/status",
        headers=auth_header(owner1),
        json={"status": "REJECTED", "remark": "Kitchen is at full capacity"}
    )
    assert res_rej.status_code == 200
    assert res_rej.json()["status"] == "REJECTED"


def test_confirmed_to_cancelled_transition(client, seed_data):
    customer1 = seed_data["customer1"]
    owner1 = seed_data["owner1"]
    rest1 = seed_data["restaurant1"]
    item1 = seed_data["item1"]
    addr1 = seed_data["address1"]

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

    client.patch(f"/orders/{order_id}/status", headers=auth_header(owner1), json={"status": "CONFIRMED"})

    res_cancel = client.patch(f"/orders/{order_id}/cancel", headers=auth_header(customer1))
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "CANCELLED"
