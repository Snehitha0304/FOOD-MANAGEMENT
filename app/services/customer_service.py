import logging
from typing import List
from sqlalchemy.orm import Session

from app.models.addresses import Address
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse
from app.schemas.customer import CustomerProfileUpdate
from app.schemas.auth import UserResponse
from app.repositories.address_repository import address_repository
from app.repositories.user_repository import user_repository
from app.core.exceptions import NotFoundException, ForbiddenException

logger = logging.getLogger("audit")


class CustomerService:
    # Profile
    def get_profile(self, db: Session, user_id: int) -> UserResponse:
        user = user_repository.get_by_id(db, user_id)
        if not user:
            raise NotFoundException("User not found", code="USER_NOT_FOUND")
        return UserResponse.model_validate(user)

    def update_profile(self, db: Session, user_id: int, data: CustomerProfileUpdate) -> UserResponse:
        user = user_repository.get_by_id(db, user_id)
        if not user:
            raise NotFoundException("User not found", code="USER_NOT_FOUND")

        update_dict = data.model_dump(exclude_unset=True)
        updated = user_repository.update(db, user, update_dict)
        logger.info(f"AUDIT: Customer {user_id} updated profile")
        return UserResponse.model_validate(updated)

    # Addresses
    def get_addresses(self, db: Session, user_id: int) -> List[AddressResponse]:
        addresses = address_repository.get_by_user_id(db, user_id)
        return [AddressResponse.model_validate(a) for a in addresses]

    def create_address(self, db: Session, user_id: int, data: AddressCreate) -> AddressResponse:
        if data.is_default:
            address_repository.clear_default_for_user(db, user_id)

        address = Address(
            user_id=user_id,
            line1=data.line1,
            line2=data.line2,
            city=data.city,
            pincode=data.pincode,
            is_default=data.is_default
        )
        created = address_repository.create(db, address)
        logger.info(f"AUDIT: Customer {user_id} created address ID {created.id}")
        return AddressResponse.model_validate(created)

    def set_default_address(self, db: Session, user_id: int, address_id: int) -> AddressResponse:
        address = address_repository.get_by_id(db, address_id)
        if not address:
            raise NotFoundException("Address not found", code="ADDRESS_NOT_FOUND")
        if address.user_id != user_id:
            raise ForbiddenException("You cannot modify another user's address", code="ADDRESS_OWNERSHIP_VIOLATION")

        address_repository.clear_default_for_user(db, user_id)
        updated = address_repository.update(db, address, {"is_default": True})
        logger.info(f"AUDIT: Customer {user_id} set address {address_id} as default")
        return AddressResponse.model_validate(updated)

    def delete_address(self, db: Session, user_id: int, address_id: int) -> None:
        address = address_repository.get_by_id(db, address_id)
        if not address:
            raise NotFoundException("Address not found", code="ADDRESS_NOT_FOUND")
        if address.user_id != user_id:
            raise ForbiddenException("You cannot delete another user's address", code="ADDRESS_OWNERSHIP_VIOLATION")

        address_repository.delete(db, address)
        logger.info(f"AUDIT: Customer {user_id} deleted address {address_id}")


customer_service = CustomerService()
