import pytest
from tests.conftest import auth_header


def test_reports_access(client, seed_data):
    owner1 = seed_data["owner1"]
    admin = seed_data["admin"]
    customer1 = seed_data["customer1"]

    # 1. Owner can access sales report
    res_owner_sales = client.get("/reports/restaurant-sales", headers=auth_header(owner1))
    assert res_owner_sales.status_code == 200
    assert "total_orders" in res_owner_sales.json()

    # 2. Admin can access sales report
    res_admin_sales = client.get("/reports/restaurant-sales", headers=auth_header(admin))
    assert res_admin_sales.status_code == 200

    # 3. Customer is forbidden from sales report
    res_cust_sales = client.get("/reports/restaurant-sales", headers=auth_header(customer1))
    assert res_cust_sales.status_code == 403

    # 4. Admin agent performance
    res_agent_perf = client.get("/reports/agent-performance", headers=auth_header(admin))
    assert res_agent_perf.status_code == 200
    assert isinstance(res_agent_perf.json(), list)

    # 5. Admin cancellation rate
    res_cancel_rate = client.get("/reports/cancellation-rate", headers=auth_header(admin))
    assert res_cancel_rate.status_code == 200
    assert "cancellation_rate_percentage" in res_cancel_rate.json()
