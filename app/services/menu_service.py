import logging
from typing import List, Dict
from sqlalchemy.orm import Session

from app.models.menu_categories import MenuCategory
from app.models.menu_items import MenuItem
from app.schemas.menu import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    MenuItemCreate,
    MenuItemUpdate,
    MenuItemAvailabilityUpdate,
    MenuItemResponse,
    CategoryWithItems,
    RestaurantMenuResponse
)
from app.repositories.menu_repository import menu_repository
from app.repositories.restaurant_repository import restaurant_repository
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException

logger = logging.getLogger("audit")


class MenuService:
    def _get_owner_restaurant(self, db: Session, owner_id: int):
        restaurant = restaurant_repository.get_by_owner_id(db, owner_id)
        if not restaurant:
            raise ForbiddenException("You must create a restaurant before managing menu items", code="RESTAURANT_REQUIRED")
        return restaurant

    # Categories
    def create_category(self, db: Session, owner_id: int, data: CategoryCreate) -> CategoryResponse:
        restaurant = self._get_owner_restaurant(db, owner_id)
        category = MenuCategory(
            restaurant_id=restaurant.id,
            name=data.name,
            display_order=data.display_order
        )
        created = menu_repository.create_category(db, category)
        logger.info(f"AUDIT: Category '{created.name}' (ID {created.id}) created for restaurant {restaurant.id} by owner {owner_id}")
        return CategoryResponse.model_validate(created)

    def get_categories(self, db: Session, owner_id: int) -> List[CategoryResponse]:
        restaurant = self._get_owner_restaurant(db, owner_id)
        categories = menu_repository.get_categories_by_restaurant(db, restaurant.id)
        return [CategoryResponse.model_validate(cat) for cat in categories]

    def update_category(self, db: Session, owner_id: int, category_id: int, data: CategoryUpdate) -> CategoryResponse:
        restaurant = self._get_owner_restaurant(db, owner_id)
        category = menu_repository.get_category_by_id(db, category_id)
        if not category:
            raise NotFoundException("Menu category not found", code="CATEGORY_NOT_FOUND")
        if category.restaurant_id != restaurant.id:
            raise ForbiddenException("You do not have permission to edit this category", code="CATEGORY_OWNERSHIP_VIOLATION")

        update_dict = data.model_dump(exclude_unset=True)
        updated = menu_repository.update_category(db, category, update_dict)
        logger.info(f"AUDIT: Category {category_id} updated by owner {owner_id}")
        return CategoryResponse.model_validate(updated)

    def delete_category(self, db: Session, owner_id: int, category_id: int) -> None:
        restaurant = self._get_owner_restaurant(db, owner_id)
        category = menu_repository.get_category_by_id(db, category_id)
        if not category:
            raise NotFoundException("Menu category not found", code="CATEGORY_NOT_FOUND")
        if category.restaurant_id != restaurant.id:
            raise ForbiddenException("You do not have permission to delete this category", code="CATEGORY_OWNERSHIP_VIOLATION")

        menu_repository.delete_category(db, category)
        logger.info(f"AUDIT: Category {category_id} deleted by owner {owner_id}")

    # Menu Items
    def create_menu_item(self, db: Session, owner_id: int, data: MenuItemCreate) -> MenuItemResponse:
        restaurant = self._get_owner_restaurant(db, owner_id)
        category = menu_repository.get_category_by_id(db, data.category_id)
        if not category or category.restaurant_id != restaurant.id:
            raise BadRequestException("Category does not belong to your restaurant", code="INVALID_CATEGORY")

        item = MenuItem(
            restaurant_id=restaurant.id,
            category_id=data.category_id,
            name=data.name,
            description=data.description,
            price=data.price,
            is_veg=data.is_veg,
            is_available=data.is_available,
            is_deleted=False
        )
        created = menu_repository.create_item(db, item)
        logger.info(f"AUDIT: MenuItem '{created.name}' (ID {created.id}) created for restaurant {restaurant.id} by owner {owner_id}")
        return MenuItemResponse.model_validate(created)

    def update_menu_item(self, db: Session, owner_id: int, item_id: int, data: MenuItemUpdate) -> MenuItemResponse:
        restaurant = self._get_owner_restaurant(db, owner_id)
        item = menu_repository.get_item_by_id(db, item_id)
        if not item:
            raise NotFoundException("Menu item not found", code="ITEM_NOT_FOUND")
        if item.restaurant_id != restaurant.id:
            raise ForbiddenException("You cannot edit another restaurant's menu items", code="ITEM_OWNERSHIP_VIOLATION")

        update_dict = data.model_dump(exclude_unset=True)
        if "category_id" in update_dict and update_dict["category_id"] is not None:
            category = menu_repository.get_category_by_id(db, update_dict["category_id"])
            if not category or category.restaurant_id != restaurant.id:
                raise BadRequestException("Category does not belong to your restaurant", code="INVALID_CATEGORY")

        updated = menu_repository.update_item(db, item, update_dict)
        logger.info(f"AUDIT: MenuItem {item_id} updated by owner {owner_id}")
        return MenuItemResponse.model_validate(updated)

    def soft_delete_menu_item(self, db: Session, owner_id: int, item_id: int) -> MenuItemResponse:
        restaurant = self._get_owner_restaurant(db, owner_id)
        item = menu_repository.get_item_by_id(db, item_id)
        if not item:
            raise NotFoundException("Menu item not found", code="ITEM_NOT_FOUND")
        if item.restaurant_id != restaurant.id:
            raise ForbiddenException("You cannot delete another restaurant's menu items", code="ITEM_OWNERSHIP_VIOLATION")

        deleted_item = menu_repository.soft_delete_item(db, item)
        logger.info(f"AUDIT: MenuItem {item_id} soft-deleted by owner {owner_id}")
        return MenuItemResponse.model_validate(deleted_item)

    def toggle_item_availability(
        self,
        db: Session,
        owner_id: int,
        item_id: int,
        data: MenuItemAvailabilityUpdate
    ) -> MenuItemResponse:
        restaurant = self._get_owner_restaurant(db, owner_id)
        item = menu_repository.get_item_by_id(db, item_id)
        if not item:
            raise NotFoundException("Menu item not found", code="ITEM_NOT_FOUND")
        if item.restaurant_id != restaurant.id:
            raise ForbiddenException("You cannot toggle another restaurant's menu items", code="ITEM_OWNERSHIP_VIOLATION")

        updated = menu_repository.update_item(db, item, {"is_available": data.is_available})
        logger.info(f"AUDIT: MenuItem {item_id} availability set to {data.is_available} by owner {owner_id}")
        return MenuItemResponse.model_validate(updated)

    def get_restaurant_menu_grouped(self, db: Session, restaurant_id: int) -> RestaurantMenuResponse:
        restaurant = restaurant_repository.get_by_id(db, restaurant_id)
        if not restaurant:
            raise NotFoundException("Restaurant not found", code="RESTAURANT_NOT_FOUND")

        categories = menu_repository.get_categories_by_restaurant(db, restaurant_id)
        items = menu_repository.get_items_by_restaurant(db, restaurant_id, include_deleted=False)

        cat_items_map: Dict[int, List[MenuItemResponse]] = {cat.id: [] for cat in categories}
        for item in items:
            if item.category_id in cat_items_map:
                cat_items_map[item.category_id].append(MenuItemResponse.model_validate(item))

        categories_grouped = [
            CategoryWithItems(
                id=cat.id,
                name=cat.name,
                display_order=cat.display_order,
                items=cat_items_map.get(cat.id, [])
            )
            for cat in categories
        ]

        return RestaurantMenuResponse(
            restaurant_id=restaurant.id,
            restaurant_name=restaurant.name,
            categories=categories_grouped
        )


menu_service = MenuService()
