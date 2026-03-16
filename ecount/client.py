"""이카운트 오픈 API 클라이언트"""

import requests
from typing import Any

from .auth import EcountAuth
from .api.inventory import InventoryAPI
from .api.sales import SalesAPI
from .api.purchase import PurchaseAPI
from .api.product import ProductAPI
from .api.customer import CustomerAPI


class EcountClient:
    """이카운트 오픈 API 메인 클라이언트"""

    def __init__(self, zone: str, com_code: str, user_id: str, api_cert_key: str):
        """
        Args:
            zone: 존 번호 (레거시 호환용, 실제 ZONE은 API로 자동 조회)
            com_code: 회사코드
            user_id: 사용자 ID
            api_cert_key: API 인증키
        """
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

        self.auth = EcountAuth(
            session=self.session,
            com_code=com_code,
            user_id=user_id,
            api_cert_key=api_cert_key,
        )

        # API 모듈
        self.inventory = InventoryAPI(client=self)
        self.sales = SalesAPI(client=self)
        self.purchase = PurchaseAPI(client=self)
        self.product = ProductAPI(client=self)
        self.customer = CustomerAPI(client=self)

    def login(self) -> str:
        """세션키를 발급받고 반환합니다."""
        return self.auth.login()

    def get(self, path: str, params: dict | None = None) -> Any:
        """GET 요청 (SESSION_ID 자동 포함)"""
        self.auth.ensure_session()
        url = f"{self.auth.base_url}{path}"
        query = {"SESSION_ID": self.auth.session_id}
        if params:
            query.update(params)
        resp = self.session.get(url, params=query)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, data: dict | None = None) -> Any:
        """POST 요청 (SESSION_ID 쿼리 파라미터로 자동 포함)"""
        self.auth.ensure_session()
        url = f"{self.auth.base_url}{path}"
        params = {"SESSION_ID": self.auth.session_id}
        resp = self.session.post(url, params=params, json=data or {})
        resp.raise_for_status()
        return resp.json()
