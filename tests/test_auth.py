import pytest
from tests.conftest import auth_header


def test_register_customer_success(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "newcustomer@test.com",
            "password": "Password@123",
            "full_name": "New Customer",
            "phone": "+919876543210"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newcustomer@test.com"
    assert data["role"] == "CUSTOMER"
    assert "id" in data


def test_register_duplicate_email(client, seed_data):
    response = client.post(
        "/auth/register",
        json={
            "email": "customer1@test.com",
            "password": "Password@123",
            "full_name": "Duplicate User",
            "phone": "+919876543210"
        }
    )
    assert response.status_code == 409
    assert response.json()["code"] == "EMAIL_ALREADY_EXISTS"


def test_register_validation_failure(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "invalid-email",
            "password": "123",
            "full_name": "A",
            "phone": "invalid"
        }
    )
    assert response.status_code == 422


def test_login_success(client, seed_data):
    response = client.post(
        "/auth/login",
        json={
            "email": "customer1@test.com",
            "password": "Customer@123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "CUSTOMER"


def test_login_invalid_password(client, seed_data):
    response = client.post(
        "/auth/login",
        json={
            "email": "customer1@test.com",
            "password": "WrongPassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "ghost@test.com",
            "password": "Password@123"
        }
    )
    assert response.status_code == 401


def test_admin_create_owner_and_agent(client, seed_data):
    admin = seed_data["admin"]
    # Create Owner
    res1 = client.post(
        "/auth/admin/users",
        headers=auth_header(admin),
        json={
            "email": "newowner@test.com",
            "password": "Password@123",
            "full_name": "New Owner",
            "phone": "+919876543299",
            "role": "RESTAURANT_OWNER"
        }
    )
    assert res1.status_code == 201
    assert res1.json()["role"] == "RESTAURANT_OWNER"

    # Create Delivery Agent
    res2 = client.post(
        "/auth/admin/users",
        headers=auth_header(admin),
        json={
            "email": "newagent@test.com",
            "password": "Password@123",
            "full_name": "New Agent",
            "phone": "+919876543298",
            "role": "DELIVERY_AGENT"
        }
    )
    assert res2.status_code == 201
    assert res2.json()["role"] == "DELIVERY_AGENT"


def test_admin_create_user_forbidden_for_customer(client, seed_data):
    customer = seed_data["customer1"]
    res = client.post(
        "/auth/admin/users",
        headers=auth_header(customer),
        json={
            "email": "shouldfail@test.com",
            "password": "Password@123",
            "full_name": "Fail User",
            "phone": "+919876543297",
            "role": "DELIVERY_AGENT"
        }
    )
    assert res.status_code == 403
