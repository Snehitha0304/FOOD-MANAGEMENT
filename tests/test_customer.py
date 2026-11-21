import pytest
from tests.conftest import auth_header


def test_customer_cannot_access_other_addresses(client, seed_data):
    customer2 = seed_data["customer2"]
    addr1 = seed_data["address1"]  # belongs to customer1

    # Attempt to set default on someone else's address
    res = client.put(f"/addresses/{addr1.id}/default", headers=auth_header(customer2))
    assert res.status_code == 403


def test_customer_cannot_delete_other_addresses(client, seed_data):
    customer2 = seed_data["customer2"]
    addr1 = seed_data["address1"]

    res = client.delete(f"/addresses/{addr1.id}", headers=auth_header(customer2))
    assert res.status_code == 403
