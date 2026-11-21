import pytest
from tests.conftest import auth_header


def test_second_owner_cannot_edit_first_owner_menu_item(client, seed_data):
    """
    Acceptance Criteria Test:
    An automated test proves a second restaurant owner cannot edit the first owner's menu items.
    """
    owner2 = seed_data["owner2"]
    item1 = seed_data["item1"]  # Belongs to restaurant 1 (owned by owner1)

    # Owner 2 attempts to edit item 1
    response = client.put(
        f"/menu-items/{item1.id}",
        headers=auth_header(owner2),
        json={"price": "999.00", "name": "Hacked Item Name"}
    )
    assert response.status_code == 403
    data = response.json()
    assert data["code"] == "ITEM_OWNERSHIP_VIOLATION"


def test_second_owner_cannot_delete_first_owner_menu_item(client, seed_data):
    owner2 = seed_data["owner2"]
    item1 = seed_data["item1"]

    response = client.delete(
        f"/menu-items/{item1.id}",
        headers=auth_header(owner2)
    )
    assert response.status_code == 403
    assert response.json()["code"] == "ITEM_OWNERSHIP_VIOLATION"


def test_second_owner_cannot_toggle_first_owner_item_availability(client, seed_data):
    owner2 = seed_data["owner2"]
    item1 = seed_data["item1"]

    response = client.patch(
        f"/menu-items/{item1.id}/availability",
        headers=auth_header(owner2),
        json={"is_available": False}
    )
    assert response.status_code == 403
    assert response.json()["code"] == "ITEM_OWNERSHIP_VIOLATION"
