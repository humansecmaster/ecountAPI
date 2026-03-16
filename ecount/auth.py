"""이카운트 API 인증 (세션키 발급/관리)"""

import requests
from typing import Optional


ZONE_API_URL = "https://oapi.ecount.com/OAPI/V2/Zone"


class EcountAuth:
    """세션키 발급 및 갱신을 담당합니다."""

    def __init__(
        self,
        session: requests.Session,
        com_code: str,
        user_id: str,
        api_cert_key: str,
        lan_type: str = "ko-KR",
    ):
        self.session = session
        self.com_code = com_code
        self.user_id = user_id
        self.api_cert_key = api_cert_key
        self.lan_type = lan_type
        self._session_id: Optional[str] = None
        self._base_url: Optional[str] = None

    def get_zone(self) -> str:
        """회사코드로 ZONE 코드를 조회합니다.

        Returns:
            ZONE 코드 (예: "AA", "CC" ...)

        Raises:
            RuntimeError: ZONE 조회 실패 시
        """
        resp = self.session.post(ZONE_API_URL, json={"COM_CODE": self.com_code})
        resp.raise_for_status()
        data = resp.json()
        if data.get("Status") != 200 or not data.get("Data", {}).get("ZONE"):
            raise RuntimeError(f"ZONE 조회 실패: {data}")
        return data["Data"]["ZONE"]

    def login(self) -> str:
        """세션키를 발급받습니다.

        Returns:
            발급된 세션 ID 문자열

        Raises:
            RuntimeError: 로그인 실패 시
        """
        zone = self.get_zone()
        login_url = f"https://sboapi{zone.lower()}.ecount.com/OAPI/V2/OAPILogin"

        payload = {
            "COM_CODE": self.com_code,
            "USER_ID": self.user_id,
            "API_CERT_KEY": self.api_cert_key,
            "LAN_TYPE": self.lan_type,
            "ZONE": zone,
        }

        resp = self.session.post(login_url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if data.get("Status") != 200 or data["Data"].get("Code") != "00":
            raise RuntimeError(f"로그인 실패: {data}")

        datas = data["Data"]["Datas"]
        self._session_id = datas["SESSION_ID"]
        self._base_url = f"https://{datas['HOST_URL']}/OAPI/V2"

        return self._session_id

    @property
    def session_id(self) -> str:
        if not self._session_id:
            raise RuntimeError("로그인이 필요합니다. login()을 먼저 호출하세요.")
        return self._session_id

    @property
    def base_url(self) -> str:
        if not self._base_url:
            raise RuntimeError("로그인이 필요합니다. login()을 먼저 호출하세요.")
        return self._base_url

    def ensure_session(self) -> None:
        """세션키가 없으면 자동으로 로그인합니다."""
        if not self._session_id:
            self.login()
