from datetime import date, datetime
from decimal import Decimal

from common.service.time_service import shift_date

PREP_WINDOW_DAYS = 14

# 最終チェックのレスポンスに載せ、通話ログ経由でダウンロードCSVの生成元になる項目。
CUSTOMER_DATA_LOG_COLUMNS = (
    "CUST_CD",
    "KYK_NO",
    "SW_CUST_KNM",
    "BIRTH_DT",
    "POST_CD",
    "TEL1",
    "TEL2",
    "ITEM",
    "PRECHG_DT",
    "NEXTCHG_DT",
    "CUST_KB",
    "SYOYU_KB",
)

ALLOWED_ITEM_PREFIXES = ("JC", "JH", "H")
CUST_KB_REGULAR_MEMBER = "4"
ALLOWED_CUST_KB_CODES = frozenset({CUST_KB_REGULAR_MEMBER})

SYOYU_KB_OWNED = "01"      # 持ち家
SYOYU_KB_RENTAL = "02"     # 賃貸
SYOYU_KB_DAITO = "03"      # 大東建託
SYOYU_KB_OSAKA_GAS = "04"  # 大阪ガス（らく得リース）
SYOYU_KB_MINI = "05"       # mini

ALLOWED_SYOYU_CODES = frozenset(
    {
        SYOYU_KB_OWNED,
        SYOYU_KB_RENTAL,
        SYOYU_KB_DAITO,
        SYOYU_KB_OSAKA_GAS,
        SYOYU_KB_MINI,
    }
)
VARIANT1_SYOYU_CODES = frozenset({SYOYU_KB_OWNED, SYOYU_KB_OSAKA_GAS})
VARIANT2_SYOYU_CODES = frozenset({SYOYU_KB_RENTAL, SYOYU_KB_DAITO})
VARIANT3_SYOYU_CODES = frozenset({SYOYU_KB_MINI})


def normalize_cust_cd(cust_cd):
    normalized = str(cust_cd or "").strip()
    if len(normalized) == 10:
        return normalized.lstrip("0")
    return normalized


def is_eligible_for_auto_cancel(item, matched_count):
    if not item:
        return False
    if matched_count != 1:
        return False
    if not str(item.get("ITEM") or "").strip().startswith(ALLOWED_ITEM_PREFIXES):
        return False
    if str(item.get("SYOYU_KB") or "").strip().zfill(2) not in ALLOWED_SYOYU_CODES:
        return False
    if str(item.get("CUST_KB") or "").strip() not in ALLOWED_CUST_KB_CODES:
        return False
    return True


def is_in_prep_window(item, today):
    nextchg_dt = item.get("NEXTCHG_DT")
    if not nextchg_dt or not today:
        return False
    prep_start = shift_date(nextchg_dt, days=-PREP_WINDOW_DAYS)
    return prep_start <= today < nextchg_dt


def classify_product_variant(item):
    syoyu = str(item.get("SYOYU_KB") or "").strip().zfill(2)
    if syoyu in VARIANT3_SYOYU_CODES:
        return 3
    if syoyu in VARIANT2_SYOYU_CODES:
        return 2
    return 1


def _to_log_value(value):
    # repository が date に変換済みの項目や DynamoDB の Decimal をそのまま返すと
    # Lambda のレスポンスが JSON 化できずに落ちるため、文字列へ寄せる。
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y%m%d")
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    return str(value).strip()


def build_customer_data_payload(item):
    if not item:
        return {}
    return {column: _to_log_value(item.get(column)) for column in CUSTOMER_DATA_LOG_COLUMNS}
