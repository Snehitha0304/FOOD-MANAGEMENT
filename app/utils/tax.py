from decimal import Decimal
from app.core.config import settings
from app.utils.pricing import round_currency


def compute_tax(amount: Decimal) -> Decimal:
    tax_percent = Decimal(str(settings.TAX_PERCENTAGE))
    return round_currency((amount * tax_percent) / Decimal("100.0"))
