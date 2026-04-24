from datetime import datetime


def require_fields(payload: dict, fields: list[str]) -> None:
    missing = [field for field in fields if field not in payload or payload[field] in (None, "")]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")


def parse_pagination(args):
    page = max(int(args.get("page", 1)), 1)
    size = min(max(int(args.get("size", 20)), 1), 100)
    return page, size


def parse_month(month_text: str | None):
    if not month_text:
        now = datetime.now()
        return now.year, now.month

    try:
        year, month = month_text.split("-")
        year, month = int(year), int(month)
        if not 1 <= month <= 12:
            raise ValueError
        return year, month
    except ValueError as exc:
        raise ValueError("month should be YYYY-MM format") from exc
