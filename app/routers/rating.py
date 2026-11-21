from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.customer import get_current_customer
from app.models.users import User
from app.schemas.rating import RatingCreate, RatingResponse
from app.services.rating_service import rating_service

router = APIRouter(tags=["Ratings"])


@router.post(
    "/orders/{id}/rating",
    response_model=RatingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Rate delivered order for restaurant and agent (User Stories 23 & 24)"
)
def rate_order(
    id: int,
    data: RatingCreate,
    customer: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    return rating_service.rate_order(db, customer.id, id, data)
