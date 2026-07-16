from dataclasses import dataclass
from datetime import datetime

# takagi(交換)側の取込フォーマットを踏襲した固定レイアウト。
# 解約フローの通話ログから埋められない列は空欄で出力する。
CUSTOMER_DATA_DOWNLOAD_OUTPUT_COLUMNS = (
    "ﾏｲﾍﾟｰｼﾞ受付日時",
    "顧客コード",
    "契約No",
    "顧客名(契約者)",
    "顧客名カナ(契約者)",
    "生年月日(契約者)",
    "電話番号1(契約者)",
    "電話番号2(契約者)",
    "郵便番号(契約者)",
    "住所1(契約者)",
    "住所2(契約者)",
    "住所3(契約者)",
    "顧客名(請求者)",
    "顧客名カナ(請求者)",
    "生年月日(請求者)",
    "電話番号1(請求者)",
    "電話番号2(請求者)",
    "郵便番号(請求者)",
    "住所1(請求者)",
    "住所2(請求者)",
    "住所3(請求者)",
    "顧客名(送付者)",
    "顧客名カナ(送付者)",
    "生年月日(送付者)",
    "電話番号1(送付者)",
    "電話番号2(送付者)",
    "郵便番号(送付者)",
    "住所1(送付者)",
    "住所2(送付者)",
    "住所3(送付者)",
    "入居開始日",
    "保証開始日",
    "品目コード(蛇口)",
    "品目コード(浄水器)",
    "蛇口シリアルNO",
    "契約品目コード(浄水器)",
    "契約次回交換日",
    "品目コード(カートリッジ)",
    "品目識別区分",
    "交換サイクル",
    "次回交換日",
    "発送方法区分",
    "支払方法区分",
    "カード会社コード",
    "カード番号1",
    "カード番号2",
    "カード番号3",
    "カード番号4",
    "カード有効期限",
    "カード名義人",
    "付加サービス(CC.CAFE)",
    "付加サービス(浄水器本体交換)",
    "付加サービス(継続割引)",
    "付加サービス(15年交換)",
    "数量",
    "メールアドレス",
    "メーリング希望有無",
)


@dataclass
class CustomerDataDownloadUrlRequestData:
    date_from: str
    date_to: str

    @staticmethod
    def _parse_download_datetime(value, field_name):
        for candidate_fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
            try:
                return datetime.strptime(value, candidate_fmt)
            except ValueError:
                continue

        raise ValueError(
            "{} は YYYY-MM-DDTHH:mm または YYYY-MM-DDTHH:mm:ss 形式で指定してください".format(
                field_name
            )
        )

    def __post_init__(self):
        normalized_date_from = str(self.date_from or "").strip()
        if not normalized_date_from:
            raise ValueError(
                "dateFrom は必須です（YYYY-MM-DDTHH:mm または YYYY-MM-DDTHH:mm:ss 形式）"
            )

        normalized_date_to = str(self.date_to or "").strip()
        if not normalized_date_to:
            raise ValueError(
                "dateTo は必須です（YYYY-MM-DDTHH:mm または YYYY-MM-DDTHH:mm:ss 形式）"
            )

        parsed_date_from = self._parse_download_datetime(
            normalized_date_from,
            field_name="dateFrom",
        )
        parsed_date_to = self._parse_download_datetime(
            normalized_date_to,
            field_name="dateTo",
        )

        if parsed_date_from > parsed_date_to:
            raise ValueError("dateFrom は dateTo 以下で指定してください")

        self.date_from = parsed_date_from.strftime("%Y-%m-%dT%H:%M:%S+09:00")
        self.date_to = parsed_date_to.strftime("%Y-%m-%dT%H:%M:%S+09:00")
