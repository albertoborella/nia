from fastapi import HTTPException, status


class NIAException(HTTPException):
    def __init__(self, code: str, message: str, status_code: int = 500):
        self.code = code
        self.message = message
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message},
        )


class AuthenticationError(NIAException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(code="AUTH_REQUIRED", message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(NIAException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(code="AUTH_FORBIDDEN", message=message, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundError(NIAException):
    def __init__(self, resource: str, resource_id: str = ""):
        detail = f"{resource} not found" if not resource_id else f"{resource} '{resource_id}' not found"
        super().__init__(code=f"NF_{resource.upper()}", message=detail, status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(NIAException):
    def __init__(self, code: str, message: str):
        super().__init__(code=code, message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ConflictError(NIAException):
    def __init__(self, message: str):
        super().__init__(code="CONFLICT_STATE", message=message, status_code=status.HTTP_409_CONFLICT)
