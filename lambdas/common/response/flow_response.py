def next_response(next_value, **data):
    return {
        "Next": next_value,
        **data,
    }


def next_yes(**data):
    return next_response("Yes", **data)


def next_no(**data):
    return next_response("No", **data)


def next_fail(**data):
    return next_response("Fail", **data)
