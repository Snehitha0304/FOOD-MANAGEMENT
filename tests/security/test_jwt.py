import pytest
from datetime import timedelta
from jose import jwt
from app.core.config import settings
from app.core.security import create_access_token


def test_jwt_token_payload_and_expiry(client, seed_data):
    customer1 = seed_data["customer1"]
    token = create_access_token(
        data={"sub": str(customer1.id), "role": customer1.role.value},
        expires_delta=timedelta(minutes=30)
    )
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert payload["sub"] == str(customer1.id)
    assert payload["role"] == "CUSTOMER"
    assert "exp" in payload


def test_jwt_expired_token(client):
    expired_token = create_access_token(
        data={"sub": "1", "role": "CUSTOMER"},
        expires_delta=timedelta(minutes=-10)
    )
    response = client.get(
        "/customer/profile",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_TOKEN"


def test_jwt_invalid_signature(client):
    fake_token = jwt.encode(
        {"sub": "1", "role": "CUSTOMER"},
        "wrong_secret_key_12345678901234567890",
        algorithm="HS256"
    )
    response = client.get(
        "/customer/profile",
        headers={"Authorization": f"Bearer {fake_token}"}
    )
    assert response.status_code == 401
