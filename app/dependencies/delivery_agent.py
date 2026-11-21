from fastapi import Depends
from app.core.security import require_role
from app.core.constants import UserRole

get_current_agent = require_role(UserRole.DELIVERY_AGENT)

__all__ = ["get_current_agent"]
