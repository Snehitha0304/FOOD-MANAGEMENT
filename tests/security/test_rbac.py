import pytest
from tests.conftest import auth_header


def test_rbac_customer_forbidden_on_owner_routes(client, seed_data):
    customer = seed_data["customer1"]
    response = client.post(
        "/restaurants/me/menu-categories",
        headers=auth_header(customer),
        json={"name": "Hacked Category"}
    )
    assert response.status_code == 403
    assert response.json()["code"] == "ROLE_NOT_AUTHORIZED"


def test_rbac_owner_forbidden_on_admin_routes(client, seed_data):
    owner = seed_data["owner1"]
    response = client.patch(
        "/orders/1/assign-agent",
        headers=auth_header(owner),
        json={"agent_id": 4}
    )
    assert response.status_code == 403
    assert response.json()["code"] == "ROLE_NOT_AUTHORIZED"


def test_rbac_agent_forbidden_on_menu_routes(client, seed_data):
    agent = seed_data["agent1"]
    item = seed_data["item1"]
    response = client.put(
        f"/menu-items/{item.id}",
        headers=auth_header(agent),
        json={"price": "100.00"}
    )
    assert response.status_code == 403
    assert response.json()["code"] == "ROLE_NOT_AUTHORIZED"


def test_unauthenticated_request_rejected(client):
    response = client.get("/customer/profile")
    assert response.status_code == 401
