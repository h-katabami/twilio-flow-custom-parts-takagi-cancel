from common.repository.cancel_flow_repository import CancelFlowRepository
from common.response.flow_response import next_no, next_response, next_yes
from common.service.flow_service import (
    matches_birthdate,
    matches_customer_code,
    matches_name,
    matches_phone,
    matches_post_code,
)
from common.service.logger import info
from common.service.time_service import get_jst, is_business_hours_now
from common.types.customer_data import (
    classify_product_variant,
    is_eligible_for_auto_cancel,
    is_in_prep_window,
)


class UseCaseError(Exception):
    pass


class JudgeCustomerCodeExistsUseCase:
    def execute(self, event_data):
        if not event_data.cust_cd:
            info("お客様ナンバーが未入力です")
            return next_no()
        repository = CancelFlowRepository()
        item = repository.get_by_cust_cd(event_data.cust_cd)
        if not item:
            info("顧客コードに一致するデータが見つかりません (cust_cd={})".format(event_data.cust_cd))
            return next_no()
        return next_yes()


class JudgePrimaryPhoneExistsUseCase:
    def execute(self, event_data):
        if not event_data.tel1:
            return next_no()
        repository = CancelFlowRepository()
        item = repository.get_by_tel(event_data.tel1)
        if not item:
            info("電話番号に一致するデータが見つかりません (tel1={})".format(event_data.tel1))
            return next_no()
        return next_yes()


class JudgeSecondaryPhoneExistsUseCase:
    def execute(self, event_data):
        if not event_data.tel2:
            return next_no()
        repository = CancelFlowRepository()
        item = repository.get_by_tel(event_data.tel2)
        if not item:
            info("電話番号2回目に一致するデータが見つかりません (tel2={})".format(event_data.tel2))
            return next_no()
        return next_yes()


class ThreePointCheckStartUseCase:
    def execute(self, event_data):
        repository = CancelFlowRepository()
        item, _ = repository.find_customer(event_data)
        if not item:
            info("三点確認1: 顧客情報が見つかりません")
            return next_yes() if is_business_hours_now() else next_no()

        cust_match = matches_customer_code(event_data, item)
        tel_match = matches_phone(event_data, item)
        post_match = matches_post_code(event_data, item)
        match_count = sum([cust_match, tel_match, post_match])
        info(
            "三点確認1: 一致点数={} (cust={}, tel={}, post={})".format(
                match_count, cust_match, tel_match, post_match
            )
        )

        if match_count >= 3:
            return next_response("Next1")
        if match_count == 2:
            return next_response("Next2")
        return next_yes() if is_business_hours_now() else next_no()


class BirthdateRegistrationCheckUseCase:
    def execute(self, event_data):
        repository = CancelFlowRepository()
        item, _ = repository.find_customer(event_data)
        if item.get("BIRTH_DT"):
            return next_yes()
        return next_no()


class ThreePointCheckBirthdateUseCase:
    def execute(self, event_data):
        repository = CancelFlowRepository()
        item, _ = repository.find_customer(event_data)
        if not item:
            info("三点確認2: 顧客情報が見つかりません")
            return next_no()

        identity_match = matches_customer_code(event_data, item) or matches_phone(
            event_data, item
        )
        post_match = matches_post_code(event_data, item)
        birth_match = matches_birthdate(event_data, item)
        match_count = sum([identity_match, post_match, birth_match])
        info(
            "三点確認2: 一致点数={} (id={}, post={}, birth={})".format(
                match_count, identity_match, post_match, birth_match
            )
        )

        if match_count >= 3:
            return next_yes()
        return next_no()


class ThreePointCheckNameUseCase:
    def execute(self, event_data):
        repository = CancelFlowRepository()
        item, _ = repository.find_customer(event_data)
        if not item:
            info("三点確認3: 顧客情報が見つかりません")
            return next_no()

        identity_match = matches_customer_code(event_data, item) or matches_phone(
            event_data, item
        )
        post_match = matches_post_code(event_data, item)
        name_match = matches_name(event_data, item)
        match_count = sum([identity_match, post_match, name_match])
        info(
            "三点確認3: 一致点数={} (id={}, post={}, name={})".format(
                match_count, identity_match, post_match, name_match
            )
        )

        if match_count >= 3:
            return next_yes()
        return next_no()


class FinalCheckUseCase:
    def execute(self, event_data):
        repository = CancelFlowRepository()
        item, matched_count = repository.find_customer(event_data)

        if not is_eligible_for_auto_cancel(item, matched_count):
            info(
                "自動受付対象外の契約です (matched_count={}, item={})".format(
                    matched_count, item.get("ITEM") if item else None
                )
            )
            if is_business_hours_now():
                return next_response("FailYes")
            return next_response("FailNo")

        today = get_jst("date")
        variant = classify_product_variant(item)
        prefix = "Yes" if is_in_prep_window(item, today) else "No"
        branch = "{}{}".format(prefix, variant)
        info("最終チェック判定: {}".format(branch))
        return next_response(branch)


class JudgeBusinessHoursUseCase:
    def execute(self, event_data):
        if is_business_hours_now():
            return next_yes()
        return next_no()
