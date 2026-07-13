import os
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")


def get_jst(kind="datetime", fmt="%Y%m%d%H%M%S", days=0, years=0):
    current = datetime.now(JST)
    if days or years:
        current = shift_date(current, days=days, years=years)

    if kind == "datetime":
        return current
    if kind == "date":
        return current.date()
    if kind == "time":
        return current.time()
    if kind == "text":
        return current.strftime(fmt)
    raise ValueError("kind must be 'datetime', 'date', 'time' or 'text'")


def is_business_hours_now():
    # 営業時間は SAM の環境変数 BUSINESS_HOURS_START / END（"HH:MM"）で固定
    now = get_jst("time")
    start_time = time.fromisoformat(os.getenv("BUSINESS_HOURS_START"))
    end_time = time.fromisoformat(os.getenv("BUSINESS_HOURS_END"))
    return start_time <= now <= end_time


def parse_text_to_date(value, fmt=None, out_fmt=None):
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    if fmt is not None:
        try:
            parsed = datetime.strptime(text, fmt)
        except ValueError:
            return None
        if out_fmt is not None:
            return parsed.strftime(out_fmt)
        return parsed.date()

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        parsed = None

    if parsed is None:
        for candidate_fmt in (
            "%Y%m%d",
            "%Y年%m月%d日",
            "%Y年%m月",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d",
            "%Y/%m",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y-%m",
        ):
            try:
                parsed = datetime.strptime(text, candidate_fmt)
                break
            except ValueError:
                continue

    if parsed is None:
        return None

    if out_fmt is not None:
        return parsed.strftime(out_fmt)
    return parsed.date()


def shift_date(base_date, days=0, years=0):
    if not base_date:
        return None

    shifted = base_date
    if years:
        try:
            shifted = shifted.replace(year=shifted.year + years)
        except ValueError:
            shifted = shifted.replace(month=2, day=28, year=shifted.year + years)

    if days:
        shifted = shifted + timedelta(days=days)

    return shifted
