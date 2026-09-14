class ApiError(Exception):
    def __init__(self, message: str, details: list[str] | None = None):
        self.message = message
        self.details = details or []
        super().__init__(message)


class ResourceNotFoundError(ApiError):
    code = "RESOURCE_NOT_FOUND"
    status_code = 404


class ConflictError(ApiError):
    code = "CONFLICT"
    status_code = 409


class BusinessRuleError(ApiError):
    code = "BUSINESS_RULE_VIOLATION"
    status_code = 400