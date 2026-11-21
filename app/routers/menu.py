from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.owner import get_current_owner
from app.models.users import User
from app.schemas.menu import (
    MenuItemUpdate,
    MenuItemAvailabilityUpdate,
    MenuItemResponse
)
from app.services.menu_service import menu_service

router = APIRouter(prefix="/menu-items", tags=["Menu Items"])


@router.put(
    "/{id}",
    response_model=MenuItemResponse,
    summary="Update menu item (User Story 8)"
)
def update_menu_item(
    id: int,
    data: MenuItemUpdate,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    return menu_service.update_menu_item(db, owner.id, id, data)


@router.delete(
    "/{id}",
    response_model=MenuItemResponse,
    summary="Soft-delete menu item (User Story 8)"
)
def soft_delete_menu_item(
    id: int,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    return menu_service.soft_delete_menu_item(db, owner.id, id)


@router.patch(
    "/{id}/availability",
    response_model=MenuItemResponse,
    summary="Toggle item availability (User Story 9)"
)
def toggle_availability(
    id: int,
    data: MenuItemAvailabilityUpdate,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    return menu_service.toggle_item_availability(db, owner.id, id, data)
