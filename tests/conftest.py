"""공통 테스트 픽스처"""

import pytest
from unittest.mock import MagicMock, patch

from ecount import EcountClient


@pytest.fixture
def mock_session():
    """requests.Session 모킹"""
    with patch("ecount.auth.requests.Session", autospec=True) as MockSession:
        yield MockSession.return_value


@pytest.fixture
def client():
    """로그인 완료된 EcountClient (HTTP 요청 모킹)"""
    with patch.object(EcountClient, "login", return_value="FAKE_SESSION_ID"):
        c = EcountClient(
            zone="AA",
            com_code="999999",
            user_id="TEST",
            api_cert_key="fake_key",
        )
        c.auth._session_id = "FAKE_SESSION_ID"
        c.auth._base_url = "https://sboapiaa.ecount.com/OAPI/V2"
        # rate limiter 간격을 0으로 설정하여 테스트 속도 향상
        c.rate_limiter._intervals = {"login": 0, "bulk": 0, "query_single": 0}
        return c


def make_success_response(data=None, status_code=200):
    """성공 응답 Mock 생성"""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = {
        "Status": 200,
        "Data": data or {"SuccessCnt": 1, "FailCnt": 0},
    }
    return resp


def make_error_response(status_code, body=None):
    """에러 응답 Mock 생성"""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = body or {}
    return resp
