from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.customer import get_current_customer
from app.models.users import User
from app.schemas.address import AddressCreate, AddressResponse
from app.schemas.customer import CustomerProfileUpdate
from app.schemas.auth import UserResponse
from app.services.customer_service import customer_service

router = APIRouter(tags=["Customer"])


# Customer Profile (User Story 13)
@router.get(
    "/customer/profile",
    response_model=UserResponse,
    summary="View customer profile (User Story 13)"
)
def get_customer_profile(
    customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    return customer_service.get_profile(db, customer.id)


@router.put(
    "/customer/profile",
    response_model=UserResponse,
    summary="Update customer profile (User Story 13)"
)
def update_customer_profile(
    data: CustomerProfileUpdate,
    customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    return customer_service.update_profile(db, customer.id, data)


# Addresses (User Story 12)
@router.get(
    "/addresses",
    response_model=List[AddressResponse],
    summary="List delivery addresses (User Story 12)"
)
def get_addresses(
    customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    return customer_service.get_addresses(db, customer.id)


@router.post(
    "/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add delivery address (User Story 12)"
)
def create_address(
    data: AddressCreate,
    customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    return customer_service.create_address(db, customer.id, data)


@router.put(
    "/addresses/{id}/default",
    response_model=AddressResponse,
    summary="Mark address as default (User Story 12)"
)
def set_default_address(
    id: int,
    customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    return customer_service.set_default_address(db, customer.id, id)


@router.delete(
    "/addresses/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete delivery address"
)
def delete_address(
    id: int,
    customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    customer_service.delete_address(db, customer.id, id)
    return None
