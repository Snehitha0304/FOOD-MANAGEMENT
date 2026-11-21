from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.users import User
from app.schemas.report import SalesReportResponse, AgentPerformanceResponse, CancellationRateResponse
from app.repositories.report_repository import report_repository
from app.repositories.restaurant_repository import restaurant_repository
from app.core.constants import UserRole
from app.core.exceptions import ForbiddenException


class ReportService:
    def get_restaurant_sales_report(
        self,
        db: Session,
        current_user: User,
        restaurant_id: Optional[int] = None
    ) -> SalesReportResponse:
        user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)

        if user_role == UserRole.RESTAURANT_OWNER.value:
            restaurant = restaurant_repository.get_by_owner_id(db, current_user.id)
            if not restaurant:
                raise ForbiddenException("You do not have a registered restaurant", code="RESTAURANT_NOT_FOUND")
            target_restaurant_id = restaurant.id
        elif user_role == UserRole.ADMIN.value:
            target_restaurant_id = restaurant_id
        else:
            raise ForbiddenException("Access denied to sales reports", code="REPORT_ACCESS_FORBIDDEN")

        data = report_repository.get_restaurant_sales(db, target_restaurant_id)
        return SalesReportResponse(**data)

    # Alias for router convenience
    get_sales_report = get_restaurant_sales_report

    def get_agent_performance_report(self, db: Session) -> List[AgentPerformanceResponse]:
        data = report_repository.get_agent_performance(db)
        return [AgentPerformanceResponse(**row) for row in data]

    def get_cancellation_rate_report(self, db: Session) -> CancellationRateResponse:
        data = report_repository.get_cancellation_rate(db)
        return CancellationRateResponse(**data)


report_service = ReportService()
