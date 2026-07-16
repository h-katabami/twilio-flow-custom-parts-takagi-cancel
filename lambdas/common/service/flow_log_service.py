"""通話ログ(1通話=1レコード)からダウンロード対象を判定する。

シナリオのエンディングノード(発送準備中Nエンディング / 解約Nエンディング)は LineOff で、
status_checkpoint も持たないためログに痕跡が残らない。
一方、各エンディングは直前の YesNo の Grammer ノードで「はい」と答えた場合にのみ到達し、
Grammer ノードの入力は user_inputs に question_id 付きで記録される。
そのため「受付完了」は下記ノードの Yes 入力で判定する。
"""

FINAL_CHECK_QUESTION_ID = "最終チェック"

# {このノードで Yes: 到達するエンディング}
# 発送準備中3 / 解約3 は Yes で「追加確認」に進むだけなので対象外。
ENDING_CONFIRMATION_QUESTION_IDS = (
    "発送準備中1",
    "発送準備中2",
    "発送準備中3追加確認",
    "解約1",
    "解約2",
    "解約3追加確認",
)

YES_INPUT_VALUES = frozenset({"yes", "はい", "ハイ", "ﾊｲ"})


def _dict_entries(row, field_name):
    entries = row.get(field_name)
    if not isinstance(entries, list):
        return []
    return [entry for entry in entries if isinstance(entry, dict)]


def _question_id(entry):
    # user_inputs は question / question_id どちらの形も観測されているため両対応。
    return str(entry.get("question_id") or entry.get("question") or "").strip()


def find_last_entry(row, field_name, question_id):
    matched = [
        entry
        for entry in _dict_entries(row, field_name)
        if _question_id(entry) == question_id
    ]
    if not matched:
        return {}
    return matched[-1]


def extract_final_check_customer_data(row):
    entry = find_last_entry(row, "api", FINAL_CHECK_QUESTION_ID)
    customer_data = (entry.get("result") or {}).get("customer_data")
    if not isinstance(customer_data, dict):
        return {}
    return customer_data


def is_yes_input(value):
    normalized = str(value or "").strip().rstrip("。").lower()
    return normalized in YES_INPUT_VALUES


def reached_ending(row):
    for question_id in ENDING_CONFIRMATION_QUESTION_IDS:
        entry = find_last_entry(row, "user_inputs", question_id)
        if entry and is_yes_input(entry.get("input")):
            return True
    return False
