from common.request.extract_flow_event import extract_event_data
from common.response.flow_response import next_fail
from common.service.logger import error, info, warn
from common.usecase.flow_judge_usecase import (
    BirthdateRegistrationCheckUseCase,
    FinalCheckUseCase,
    JudgeBusinessHoursUseCase,
    JudgeCustomerCodeExistsUseCase,
    JudgePrimaryPhoneExistsUseCase,
    JudgeSecondaryPhoneExistsUseCase,
    ThreePointCheckBirthdateUseCase,
    ThreePointCheckNameUseCase,
    ThreePointCheckStartUseCase,
    UseCaseError,
)

def lambda_handler(event, context):
    info("function arn: {}".format(getattr(context, "invoked_function_arn", None)))
    info("received event", event=event)
    try:
        event_data = extract_event_data(event)
        info("case: {}".format(event_data.flow_id))

        if event_data.flow_id == "お客様ナンバー照合":
            result = JudgeCustomerCodeExistsUseCase().execute(event_data)
        elif event_data.flow_id == "電話番号照合1":
            result = JudgePrimaryPhoneExistsUseCase().execute(event_data)
        elif event_data.flow_id == "電話番号照合2":
            result = JudgeSecondaryPhoneExistsUseCase().execute(event_data)
        elif event_data.flow_id == "三点確認1":
            result = ThreePointCheckStartUseCase().execute(event_data)
        elif event_data.flow_id == "生年月日登録確認":
            result = BirthdateRegistrationCheckUseCase().execute(event_data)
        elif event_data.flow_id == "三点確認2":
            result = ThreePointCheckBirthdateUseCase().execute(event_data)
        elif event_data.flow_id == "三点確認3":
            result = ThreePointCheckNameUseCase().execute(event_data)
        elif event_data.flow_id == "最終チェック":
            result = FinalCheckUseCase().execute(event_data)
        elif event_data.flow_id.startswith("営業時間確認"):
            result = JudgeBusinessHoursUseCase().execute(event_data)
        else:
            raise UseCaseError("unsupported_flow_id:{}".format(event_data.flow_id))

        info("result: {}".format(result))
        return result
    except UseCaseError as exc:
        warn("usecase error: {}".format(exc))
        return next_fail()
    except Exception as exc:
        error("unhandled error: {}".format(exc), exc=exc)
        return next_fail()
