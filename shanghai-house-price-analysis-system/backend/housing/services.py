from decimal import Decimal

from django.db.models import Avg, Count, Max, Min

from housing.models import Community, Listing, PredictionResult


def _to_decimal(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def get_district_stats() -> list[dict]:
    rows = (
        Listing.objects.values("district")
        .annotate(
            listing_count=Count("id"),
            avg_unit_price=Avg("unit_price"),
            avg_total_price=Avg("total_price"),
            avg_area=Avg("area"),
        )
        .order_by("-avg_unit_price", "district")
    )
    return [
        {
            "district": row["district"],
            "listing_count": row["listing_count"],
            "avg_unit_price": round(_to_decimal(row["avg_unit_price"]), 2),
            "avg_total_price": round(_to_decimal(row["avg_total_price"]), 2),
            "avg_area": round(_to_decimal(row["avg_area"]), 2),
        }
        for row in rows
    ]


def build_overview_payload() -> dict:
    listing_stats = Listing.objects.aggregate(
        listing_count=Count("id"),
        avg_unit_price=Avg("unit_price"),
        avg_total_price=Avg("total_price"),
        price_min=Min("unit_price"),
        price_max=Max("unit_price"),
    )
    predictions = list(
        PredictionResult.objects.values(
            "target_level",
            "target_name",
            "model_name",
            "predicted_unit_price",
        )[:5]
    )
    return {
        "metrics": {
            "listing_count": listing_stats["listing_count"] or 0,
            "community_count": Community.objects.count(),
            "avg_unit_price": round(_to_decimal(listing_stats["avg_unit_price"]), 2),
            "avg_total_price": round(_to_decimal(listing_stats["avg_total_price"]), 2),
            "price_min": round(_to_decimal(listing_stats["price_min"]), 2),
            "price_max": round(_to_decimal(listing_stats["price_max"]), 2),
        },
        "charts": {
            "district_distribution": get_district_stats(),
            "latest_predictions": [
                {
                    **item,
                    "predicted_unit_price": round(_to_decimal(item["predicted_unit_price"]), 2),
                }
                for item in predictions
            ],
        },
    }
