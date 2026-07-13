import difflib

from common.service.time_service import parse_text_to_date


def is_name_match(input_name, source_name, threshold=0.5):
    input_text = str(input_name or "")
    source_text = str(source_name or "")

    for suffix in ("デス", "デイス", "デエス"):
        if input_text.endswith(suffix):
            input_text = input_text[: -len(suffix)]
            break

    for suffix in ("デス", "デイス", "デエス"):
        if source_text.endswith(suffix):
            source_text = source_text[: -len(suffix)]
            break

    if not input_text or not source_text:
        return False
    matcher = difflib.SequenceMatcher(None, input_text, source_text).ratio()
    return matcher >= threshold


def is_birthdate_match(input_birthdate, source_birthdate):
    parsed_input = parse_text_to_date(input_birthdate)
    parsed_source = parse_text_to_date(source_birthdate)
    if parsed_input is None or parsed_source is None:
        return False
    return parsed_input == parsed_source


def is_post_code_match(input_post_cd, source_post_cd):
    input_text = str(input_post_cd or "").replace("-", "").strip()
    source_text = str(source_post_cd or "").strip()
    if not input_text or not source_text:
        return False
    return input_text == source_text


def is_phone_match(input_tel, item):
    tel = str(input_tel or "").strip()
    if not tel:
        return False
    return item.get("TEL1") == tel or item.get("TEL2") == tel


def matches_customer_code(event_data, item):
    return bool(event_data.cust_cd) and (
        str(item.get("CUST_CD") or "").strip() == event_data.cust_cd
    )


def matches_phone(event_data, item):
    return is_phone_match(event_data.tel1, item) or is_phone_match(
        event_data.tel2, item
    )


def matches_post_code(event_data, item):
    return is_post_code_match(event_data.post_cd, item.get("POST_CD"))


def matches_birthdate(event_data, item):
    return is_birthdate_match(event_data.birthdate, item.get("BIRTH_DT"))


def matches_name(event_data, item):
    return is_name_match(event_data.sw_cust_knm, item.get("SW_CUST_KNM"))
