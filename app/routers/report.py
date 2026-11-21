from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.core.constants import UserRole
from app.models.users import User
from app.schemas.report import SalesReportResponse, AgentPerformanceResponse, CancellationRateResponse
from app.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/restaurant-sales",
    response_model=SalesReportResponse,
    summary="Get restaurant sales report (RESTAURANT_OWNER / ADMIN)"
)
def get_restaurant_sales(
    restaurant_id: Optional[int] = Query(None, description="Restaurant ID (Admin only)"),
    current_user: User = Depends(require_role(UserRole.RESTAURANT_OWNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    return report_service.get_sales_report(db, current_user, restaurant_id)


@router.get(
    "/agent-performance",
    response_model=List[AgentPerformanceResponse],
    summary="Get delivery agent performance report (ADMIN)"
)
def get_agent_performance(
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    return report_service.get_agent_performance_report(db)


@router.get(
    "/cancellation-rate",
    response_model=CancellationRateResponse,
    summary="Get platform cancellation and rejection rate report (ADMIN)"
)
def get_cancellation_rate(
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    return report_service.get_cancellation_rate_report(db)
