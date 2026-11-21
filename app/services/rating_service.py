import logging
from sqlalchemy.orm import Session

from app.models.ratings import Rating
from app.schemas.rating import RatingCreate, RatingResponse
from app.core.constants import OrderStatus
from app.repositories.rating_repository import rating_repository
from app.repositories.order_repository import order_repository
from app.repositories.restaurant_repository import restaurant_repository
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    ForbiddenException,
    ConflictException
)

logger = logging.getLogger("audit")


class RatingService:
    def rate_order(self, db: Session, customer_id: int, order_id: int, data: RatingCreate) -> RatingResponse:
        order = order_repository.get_by_id(db, order_id)
        if not order:
            raise NotFoundException("Order not found", code="ORDER_NOT_FOUND")

        # Rule 7a: Only by ordering customer
        if order.customer_id != customer_id:
            raise ForbiddenException("Only the customer who placed the order can rate it", code="RATING_FORBIDDEN")

        # Rule 7b: Only for a DELIVERED order
        if order.status != OrderStatus.DELIVERED:
            raise BadRequestException(
                f"Cannot rate an order that is not DELIVERED. Current status: '{order.status.value}'",
                code="ORDER_NOT_DELIVERED"
            )

        # Rule 7c: Submitted only once
        existing_rating = rating_repository.get_by_order_id(db, order_id)
        if existing_rating:
            raise ConflictException("Rating has already been submitted for this order", code="RATING_ALREADY_EXISTS")

        rating = Rating(
            order_id=order.id,
            restaurant_rating=data.restaurant_rating,
            agent_rating=data.agent_rating,
            comment=data.comment
        )
        created_rating = rating_repository.create(db, rating)

        # Rule 8: The restaurant's average rating is recomputed on each new rating
        new_avg = rating_repository.get_restaurant_average_rating(db, order.restaurant_id)
        restaurant_repository.update_avg_rating(db, order.restaurant_id, new_avg)

        logger.info(f"AUDIT: Rating submitted for order {order.id} by customer {customer_id}. New restaurant avg: {new_avg}")
        return RatingResponse.model_validate(created_rating)


rating_service = RatingService()
