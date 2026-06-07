from datetime import datetime


def non_empty(value: str, field: str) -> str:
    value = (value or "").strip()
    if not value:
        raise ValueError(f"{field} cannot be empty")
    return value


def parse_date(value: str, field: str):
    value = (value or "").strip()
    for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"{field} must be DD-MM-YYYY")


def format_date(value) -> str:
    if isinstance(value, str):
        value = parse_date(value, "Date")
    return value.strftime("%d-%m-%Y")