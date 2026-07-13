from dataclasses import dataclass, field

from common.types.customer_data import normalize_cust_cd


@dataclass
class CancelEventData:
    flow_id: str
    cust_cd: str = ""
    tel1: str = ""
    tel2: str = ""
    post_cd: str = ""
    birthdate: str = ""
    sw_cust_knm: str = ""
    raw_event: dict = field(default_factory=dict)

    def __post_init__(self):
        self.flow_id = str(self.flow_id or "")
        self.cust_cd = normalize_cust_cd(self.cust_cd)
        self.tel1 = str(self.tel1 or "").strip()
        self.tel2 = str(self.tel2 or "").strip()
        self.post_cd = str(self.post_cd or "").strip()
        self.birthdate = str(self.birthdate or "").strip()
        self.sw_cust_knm = str(self.sw_cust_knm or "").strip()
        self.raw_event = self.raw_event if isinstance(self.raw_event, dict) else {}
