import pytest
from tests.conftest import auth_header


def test_invalid_transitions_return_409_conflict(client, seed_data):
    """
    Acceptance Criteria Test:
    Any transition not in the state machine must return 409 Conflict.
    """
    customer1 = seed_data["customer1"]
    owner1 = seed_data["owner1"]
    rest1 = seed_data["restaurant1"]
    item1 = seed_data["item1"]
    addr1 = seed_data["address1"]

    # Place order (Status: PLACED)
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

    # 1. Invalid: PLACED -> PREPARING (skipping CONFIRMED) -> 409
    res_inv1 = client.patch(
        f"/orders/{order_id}/status",
        headers=auth_header(owner1),
        json={"status": "PREPARING"}
    )
    assert res_inv1.status_code == 409
    assert res_inv1.json()["code"] == "INVALID_STATUS_TRANSITION"

    # 2. Invalid: PLACED -> READY_FOR_PICKUP -> 409
    res_inv2 = client.patch(
        f"/orders/{order_id}/status",
        headers=auth_header(owner1),
        json={"status": "READY_FOR_PICKUP"}
    )
    assert res_inv2.status_code == 409

    # 3. Cancel order (moves to CANCELLED)
    res_cancel = client.patch(f"/orders/{order_id}/cancel", headers=auth_header(customer1))
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "CANCELLED"

    # 4. Invalid: CANCELLED -> CONFIRMED -> 409
    res_inv3 = client.patch(
        f"/orders/{order_id}/status",
        headers=auth_header(owner1),
        json={"status": "CONFIRMED"}
    )
    assert res_inv3.status_code == 409
