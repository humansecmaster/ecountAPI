"""API 모듈 공통 베이스 클래스"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..client import EcountClient


class BaseAPI:
    def __init__(self, client: "EcountClient"):
        self._client = client

    def get(self, path: str, params: dict | None = None) -> Any:
        return self._client.get(path, params=params)

    def post(self, path: str, data: dict | None = None) -> Any:
        return self._client.post(path, data=data)
