import pytest
from tests.conftest import auth_header


def test_customer_addresses_lifecycle(client, seed_data):
    customer1 = seed_data["customer1"]

    # 1. Create address
    res = client.post(
        "/addresses",
        headers=auth_header(customer1),
        json={
            "line1": "Flat 502, Tower 3",
            "line2": "HSR Layout",
            "city": "Bengaluru",
            "pincode": "560102",
            "is_default": False
        }
    )
    assert res.status_code == 201
    addr_id = res.json()["id"]

    # 2. List addresses
    res_list = client.get("/addresses", headers=auth_header(customer1))
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 2

    # 3. Mark default
    res_def = client.put(f"/addresses/{addr_id}/default", headers=auth_header(customer1))
    assert res_def.status_code == 200
    assert res_def.json()["is_default"] is True

    # 4. Delete address
    res_del = client.delete(f"/addresses/{addr_id}", headers=auth_header(customer1))
    assert res_del.status_code == 204


def test_customer_profile(client, seed_data):
    customer1 = seed_data["customer1"]

    # Get profile
    res_get = client.get("/customer/profile", headers=auth_header(customer1))
    assert res_get.status_code == 200
    assert res_get.json()["email"] == "customer1@test.com"

    # Update profile
    res_up = client.put(
        "/customer/profile",
        headers=auth_header(customer1),
        json={"full_name": "Aarav Updated"}
    )
    assert res_up.status_code == 200
    assert res_up.json()["full_name"] == "Aarav Updated"
