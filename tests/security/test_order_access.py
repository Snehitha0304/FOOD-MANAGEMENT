import pytest
from tests.conftest import auth_header


def test_order_participant_only_access_control(client, seed_data):
    """
    Security Requirement Test:
    GET /orders/{id} must be accessible only to the ordering customer,
    the restaurant owner who received it, the assigned agent, and an admin.
    """
    customer1 = seed_data["customer1"]
    customer2 = seed_data["customer2"]
    owner1 = seed_data["owner1"]
    owner2 = seed_data["owner2"]
    agent1 = seed_data["agent1"]
    admin = seed_data["admin"]
    rest1 = seed_data["restaurant1"]
    item1 = seed_data["item1"]
    addr1 = seed_data["address1"]

    # Customer 1 places order
    order_res = client.post(
        "/orders",
        headers=auth_header(customer1),
        json={
            "restaurant_id": rest1.id,
            "address_id": addr1.id,
            "items": [{"menu_item_id": item1.id, "quantity": 1}]
        }
    )
    order_id = order_res.json()["id"]

    # 1. Ordering Customer can access
    res_c1 = client.get(f"/orders/{order_id}", headers=auth_header(customer1))
    assert res_c1.status_code == 200

    # 2. Receiving Restaurant Owner can access
    res_o1 = client.get(f"/orders/{order_id}", headers=auth_header(owner1))
    assert res_o1.status_code == 200

    # 3. Admin can access
    res_adm = client.get(f"/orders/{order_id}", headers=auth_header(admin))
    assert res_adm.status_code == 200

    # 4. Another customer CANNOT access (IDOR prevention)
    res_c2 = client.get(f"/orders/{order_id}", headers=auth_header(customer2))
    assert res_c2.status_code == 403
    assert res_c2.json()["code"] == "ORDER_ACCESS_FORBIDDEN"

    # 5. Another restaurant owner CANNOT access
    res_o2 = client.get(f"/orders/{order_id}", headers=auth_header(owner2))
    assert res_o2.status_code == 403

    # 6. Unassigned agent CANNOT access
    res_ag_un = client.get(f"/orders/{order_id}", headers=auth_header(agent1))
    assert res_ag_un.status_code == 403

    # Now move to READY_FOR_PICKUP and assign agent1
    client.patch(f"/orders/{order_id}/status", headers=auth_header(owner1), json={"status": "CONFIRMED"})
    client.patch(f"/orders/{order_id}/status", headers=auth_header(owner1), json={"status": "PREPARING"})
    client.patch(f"/orders/{order_id}/status", headers=auth_header(owner1), json={"status": "READY_FOR_PICKUP"})
    client.patch(f"/orders/{order_id}/assign-agent", headers=auth_header(admin), json={"agent_id": agent1.id})

    # 7. Assigned agent CAN now access
    res_ag_assigned = client.get(f"/orders/{order_id}", headers=auth_header(agent1))
    assert res_ag_assigned.status_code == 200
