"""이카운트 API 커스텀 예외 클래스"""


class EcountError(Exception):
    """이카운트 API 기본 예외"""

    def __init__(self, message: str, status: int | None = None, data: dict | None = None):
        self.status = status
        self.data = data or {}
        self.trace_id = self.data.get("TRACE_ID")
        super().__init__(message)


class AuthenticationError(EcountError):
    """인증 실패 (잘못된 인증키, 미수차단, IP 차단 등)"""


class SessionExpiredError(EcountError):
    """세션 만료 - 자동 재로그인 필요"""


class RateLimitError(EcountError):
    """API 전송 횟수 기준 초과 (HTTP 412 또는 연속 오류 제한)"""

    def __init__(self, message: str, retry_after: float | None = None, **kwargs):
        self.retry_after = retry_after
        super().__init__(message, **kwargs)


class ValidationError(EcountError):
    """유효성 검사 실패 - 잘못된 파라미터"""

    def __init__(self, message: str, fields: list | None = None, **kwargs):
        self.fields = fields or []
        super().__init__(message, **kwargs)


class ServerError(EcountError):
    """ECOUNT 서버 내부 오류 (HTTP 500)"""


class NotFoundError(EcountError):
    """존재하지 않는 API 경로 (HTTP 404)"""
