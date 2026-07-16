def is_company_allowed(event, allowed_companies):
    claims = (
        (event or {}).get("requestContext", {}).get("authorizer", {}).get("claims", {})
    )
    company = claims.get("custom:company")
    if company is None:
        return True
    normalized_company = str(company).lower()
    normalized_allowed = {str(name).lower() for name in allowed_companies}
    return normalized_company in normalized_allowed
