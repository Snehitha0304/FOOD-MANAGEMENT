from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.owner import get_current_owner
from app.models.users import User
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantUpdate,
    RestaurantOpenStatusUpdate,
    RestaurantResponse
)
from app.schemas.menu import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    MenuItemCreate,
    MenuItemResponse,
    RestaurantMenuResponse
)
from app.core.pagination import PageParams, PaginatedResponse
from app.services.restaurant_service import restaurant_service
from app.services.menu_service import menu_service

router = APIRouter(tags=["Restaurants"])


@router.post(
    "/restaurants",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create restaurant profile (User Story 5)"
)
def create_restaurant(
    data: RestaurantCreate,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    return restaurant_service.create_restaurant(db, owner.id, data)


@router.get(
    "/restaurants/me",
    response_model=RestaurantResponse,
    summary="Get current owner's restaurant profile"
)
def get_my_restaurant(
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    return restaurant_service.get_my_restaurant(db, owner.id)


@router.put(
    "/restaurants/me",
    response_model=RestaurantResponse,
    summary="Update restaurant profile (User Story 5)"
)
def update_my_restaurant(
    data: RestaurantUpdate,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    return restaurant_service.update_my_restaurant(db, owner.id, data)


@router.patch(
    "/restaurants/me/open-status",
    response_model=RestaurantResponse,
    summary="Mark restaurant open or closed (User Story 6)"
)
def set_open_status(
    data: RestaurantOpenStatusUpdate,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    return restaurant_service.set_open_status(db, owner.id, data)


@router.get(
    "/restaurants",
    response_model=PaginatedResponse[RestaurantResponse],
    summary="Search restaurants by name, cuisine, city with pagination (User Story 10)"
)
def search_restaurants(
    city: Optional[str] = Query(None, description="Filter by city"),
    cuisine: Optional[str] = Query(None, description="Filter by cuisine"),
    name: Optional[str] = Query(None, description="Filter by restaurant name"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    params = PageParams(page=page, size=size)
    return restaurant_service.search_restaurants(db, city=city, cuisine=cuisine, name=name, params=params)


@router.get(
    "/restaurants/{id}",
    response_model=RestaurantResponse,
    summary="Get restaurant details including average rating (User Story 24)"
)
def get_restaurant_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    return restaurant_service.get_restaurant_by_id(db, id)


@router.get(
    "/restaurants/{id}/menu",
    response_model=RestaurantMenuResponse,
    summary="View a restaurant's menu grouped by category (User Story 11)"
)
def get_restaurant_menu(
    id: int,
    db: Session = Depends(get_db)
):
    return menu_service.get_restaurant_menu_grouped(db, id)


# Menu Category endpoints per case study spec
@router.post(
    "/restaurants/me/menu-categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Manage menu categories - Create (User Story 7)"
)
def create_category(
    data: CategoryCreate,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    return menu_service.create_category(db, owner.id, data)


@router.get(
    "/restaurants/me/menu-categories",
    response_model=list[CategoryResponse],
    summary="Manage menu categories - List (User Story 7)"
)
def get_categories(
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    return menu_service.get_categories(db, owner.id)


@router.put(
    "/restaurants/me/menu-categories/{category_id}",
    response_model=CategoryResponse,
    summary="Manage menu categories - Update (User Story 7)"
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    return menu_service.update_category(db, owner.id, category_id, data)


@router.delete(
    "/restaurants/me/menu-categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Manage menu categories - Delete (User Story 7)"
)
def delete_category(
    category_id: int,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    menu_service.delete_category(db, owner.id, category_id)
    return None


@router.post(
    "/restaurants/me/menu-items",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add menu item (User Story 8)"
)
def create_menu_item(
    data: MenuItemCreate,
    owner: User = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    return menu_service.create_menu_item(db, owner.id, data)
