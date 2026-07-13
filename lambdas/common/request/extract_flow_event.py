from common.types.event_data import CancelEventData


def extract_event_data(event):
    payload = event if isinstance(event, dict) else {}
    flow_id = payload.get("flow_id")
    cust_cd = payload.get("お客様ナンバー")
    tel1 = payload.get("電話番号(照合あり)") or payload.get("電話番号(照合なし)")
    tel2 = payload.get("電話番号(2回目)")
    post_cd = payload.get("郵便番号(照合あり)") or payload.get("郵便番号(照合なし)")
    birthdate = payload.get("生年月日確認")
    sw_cust_knm = payload.get("名前確認")

    return CancelEventData(
        flow_id=flow_id,
        cust_cd=cust_cd,
        tel1=tel1,
        tel2=tel2,
        post_cd=post_cd,
        birthdate=birthdate,
        sw_cust_knm=sw_cust_knm,
        raw_event=event if isinstance(event, dict) else {},
    )
