"""이카운트 오픈 API 클라이언트"""

import requests
from typing import Any

from .auth import EcountAuth
from .exceptions import (
    EcountError,
    RateLimitError,
    SessionExpiredError,
    ValidationError,
    ServerError,
    NotFoundError,
)
from .rate_limiter import RateLimiter
from .api.inventory import InventoryAPI
from .api.sales import SalesAPI
from .api.purchase import PurchaseAPI
from .api.product import ProductAPI
from .api.customer import CustomerAPI
from .api.invoice import InvoiceAPI
from .api.etax import ETaxInvoiceAPI


class EcountClient:
    """이카운트 오픈 API 메인 클라이언트"""

    def __init__(
        self,
        zone: str,
        com_code: str,
        user_id: str,
        api_cert_key: str,
        auto_retry: bool = True,
        test_mode: bool = False,
    ):
        """
        Args:
            zone: 존 번호 (레거시 호환용, 실제 ZONE은 API로 자동 조회)
            com_code: 회사코드
            user_id: 사용자 ID
            api_cert_key: API 인증키
            auto_retry: 세션 만료 시 자동 재로그인 여부
            test_mode: 테스트 모드 (http://sboapi.ecount.com 사용)
        """
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.auto_retry = auto_retry

        self.auth = EcountAuth(
            session=self.session,
            com_code=com_code,
            user_id=user_id,
            api_cert_key=api_cert_key,
            test_mode=test_mode,
        )

        self.rate_limiter = RateLimiter()

        # API 모듈
        self.inventory = InventoryAPI(client=self)
        self.sales = SalesAPI(client=self)
        self.purchase = PurchaseAPI(client=self)
        self.product = ProductAPI(client=self)
        self.customer = CustomerAPI(client=self)
        self.invoice = InvoiceAPI(client=self)
        self.etax = ETaxInvoiceAPI(client=self)

    def login(self) -> str:
        """세션키를 발급받고 반환합니다."""
        self.rate_limiter.wait("login")
        return self.auth.login()

    def _check_response(self, resp: requests.Response, path: str) -> dict:
        """API 응답을 검사하고 에러 시 적절한 예외를 발생시킵니다."""
        http_status = resp.status_code

        if http_status == 404:
            raise NotFoundError(
                f"존재하지 않는 API: {path}",
                status=404,
            )

        if http_status == 412:
            raise RateLimitError(
                f"API 전송 횟수 기준 초과: {path}",
                status=412,
                retry_after=10.0,
            )

        if http_status == 500:
            try:
                data = resp.json()
            except Exception:
                data = {}
            raise ServerError(
                f"서버 내부 오류: {path}",
                status=500,
                data=data,
            )

        # 200이지만 비즈니스 로직 에러가 있을 수 있음
        try:
            data = resp.json()
        except Exception:
            resp.raise_for_status()
            return {}

        status = data.get("Status")

        # 세션 만료 감지
        if status == 500:
            message = data.get("Message", "")
            if "Session" in message or "Timeout" in message:
                raise SessionExpiredError(
                    f"세션 만료: {message}",
                    status=500,
                    data=data,
                )
            # 유효성 검사 실패 (Status 500 + 실패 컬럼 목록)
            errors = data.get("Errors", [])
            if errors:
                fields = [e.get("Field", e.get("Message", "")) for e in errors]
                raise ValidationError(
                    f"유효성 검사 실패: {fields}",
                    fields=fields,
                    status=500,
                    data=data,
                )
            raise ServerError(
                f"서버 오류: {data.get('Message', '알 수 없는 오류')}",
                status=500,
                data=data,
            )

        # Status 200인데 FailCnt > 0인 경우 (부분 실패)
        result_data = data.get("Data", {})
        if isinstance(result_data, dict) and result_data.get("FailCnt", 0) > 0:
            details = result_data.get("ResultDetails", [])
            fail_msgs = [
                d.get("Message", "") for d in details
                if not d.get("IsSuccess", True)
            ]
            if fail_msgs:
                raise ValidationError(
                    f"입력 실패 {result_data['FailCnt']}건: {fail_msgs}",
                    fields=fail_msgs,
                    status=200,
                    data=data,
                )

        return data

    def get(self, path: str, params: dict | None = None) -> Any:
        """GET 요청 (SESSION_ID 자동 포함)"""
        self.auth.ensure_session()
        self.rate_limiter.wait(self._api_category(path))
        url = f"{self.auth.base_url}{path}"
        query = {"SESSION_ID": self.auth.session_id}
        if params:
            query.update(params)

        resp = self.session.get(url, params=query)
        try:
            return self._check_response(resp, path)
        except SessionExpiredError:
            if self.auto_retry:
                self.auth.login()
                query["SESSION_ID"] = self.auth.session_id
                resp = self.session.get(url, params=query)
                return self._check_response(resp, path)
            raise

    def post(self, path: str, data: dict | None = None) -> Any:
        """POST 요청 (SESSION_ID 쿼리 파라미터로 자동 포함)"""
        self.auth.ensure_session()
        self.rate_limiter.wait(self._api_category(path))
        url = f"{self.auth.base_url}{path}"
        params = {"SESSION_ID": self.auth.session_id}

        resp = self.session.post(url, params=params, json=data or {})
        try:
            return self._check_response(resp, path)
        except SessionExpiredError:
            if self.auto_retry:
                self.auth.login()
                params["SESSION_ID"] = self.auth.session_id
                resp = self.session.post(url, params=params, json=data or {})
                return self._check_response(resp, path)
            raise

    @staticmethod
    def _api_category(path: str) -> str:
        """API 경로에서 rate limit 카테고리를 결정합니다."""
        path_lower = path.lower()
        # 단건 조회 API (1회/1초)
        single_keywords = [
            "getbasicproduct",      # 품목조회(단건) - GetBasicProducts 와 구분
            "getlistinventory",     # 재고현황(단건)
            "getlistinventorywh",   # 창고별재고현황(단건)
        ]
        for kw in single_keywords:
            if kw in path_lower and "list" not in path_lower.replace(kw, ""):
                return "query_single"

        # 입력/조회 API (1회/10초)
        return "bulk"
