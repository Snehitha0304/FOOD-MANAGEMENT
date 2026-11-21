import pytest
from decimal import Decimal
from tests.conftest import auth_header


def test_tampered_price_in_request_body_does_not_affect_computed_total(client, seed_data):
    """
    Acceptance Criteria Test:
    A tampered price in the request body does not affect the computed total.
    Item 1 has real price 250.00.
    Client submits tampered price 1.00 in the payload.
    Server MUST calculate grand total using the catalog price (250.00), not the tampered price (1.00).
    """
    customer1 = seed_data["customer1"]
    rest1 = seed_data["restaurant1"]
    item1 = seed_data["item1"]  # actual catalog price: 250.00
    addr1 = seed_data["address1"]

    tampered_payload = {
        "restaurant_id": rest1.id,
        "address_id": addr1.id,
        "items": [
            {
                "menu_item_id": item1.id,
                "quantity": 2,
                "price": "1.00"  # Tampered price!
            }
        ]
    }

    response = client.post(
        "/orders",
        headers=auth_header(customer1),
        json=tampered_payload
    )
    assert response.status_code == 201
    order = response.json()

    # Real catalog item total = 250.00 * 2 = 500.00
    # Tax = 5% of 500 = 25.00
    # Delivery fee: 500 >= 500 -> free (0.00)
    # Grand total = 500.00 + 25.00 = 525.00
    # If tampered price 1.00 was used, item total would be 2.00, which is wrong!
    assert Decimal(str(order["item_total"])) == Decimal("500.00")
    assert Decimal(str(order["grand_total"])) == Decimal("525.00")
