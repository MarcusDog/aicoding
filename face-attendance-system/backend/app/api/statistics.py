from flask import Blueprint, request

from ..services.statistics_service import StatisticsService
from ..utils.decorators import admin_required
from ..utils.response import success_response

statistics_bp = Blueprint("statistics", __name__, url_prefix="/statistics")


@statistics_bp.get("/monthly")
@admin_required
def monthly():
    month = request.args.get("month")
    return success_response(StatisticsService.month_summary(month))
