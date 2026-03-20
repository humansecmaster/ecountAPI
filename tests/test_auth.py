"""인증 모듈 테스트"""

import pytest
from unittest.mock import MagicMock, patch

from ecount.auth import EcountAuth


@pytest.fixture
def auth():
    session = MagicMock()
    return EcountAuth(
        session=session,
        com_code="999999",
        user_id="TEST",
        api_cert_key="fake_key",
    )


class TestGetZone:

    def test_success(self, auth):
        auth.session.post.return_value.json.return_value = {
            "Status": 200,
            "Data": {"ZONE": "AA"},
        }
        assert auth.get_zone() == "AA"

    def test_failure_raises(self, auth):
        auth.session.post.return_value.json.return_value = {
            "Status": 500,
            "Data": {},
        }
        with pytest.raises(RuntimeError, match="ZONE 조회 실패"):
            auth.get_zone()


class TestLogin:

    def test_success(self, auth):
        auth.session.post.return_value.json.side_effect = [
            # get_zone 응답
            {"Status": 200, "Data": {"ZONE": "AA"}},
            # login 응답
            {
                "Status": 200,
                "Data": {
                    "Code": "00",
                    "Datas": {
                        "SESSION_ID": "test_session_123",
                        "HOST_URL": "sboapiaa.ecount.com",
                    },
                },
            },
        ]
        result = auth.login()
        assert result == "test_session_123"
        assert auth.session_id == "test_session_123"
        assert "sboapiaa" in auth.base_url

    def test_failure_raises(self, auth):
        auth.session.post.return_value.json.side_effect = [
            {"Status": 200, "Data": {"ZONE": "AA"}},
            {"Status": 500, "Data": {"Code": "99"}},
        ]
        with pytest.raises(RuntimeError, match="로그인 실패"):
            auth.login()


class TestSessionProperties:

    def test_session_id_without_login_raises(self, auth):
        with pytest.raises(RuntimeError, match="로그인이 필요"):
            _ = auth.session_id

    def test_base_url_without_login_raises(self, auth):
        with pytest.raises(RuntimeError, match="로그인이 필요"):
            _ = auth.base_url

    def test_ensure_session_auto_login(self, auth):
        auth.session.post.return_value.json.side_effect = [
            {"Status": 200, "Data": {"ZONE": "AA"}},
            {
                "Status": 200,
                "Data": {
                    "Code": "00",
                    "Datas": {
                        "SESSION_ID": "auto_session",
                        "HOST_URL": "sboapiaa.ecount.com",
                    },
                },
            },
        ]
        auth.ensure_session()
        assert auth.session_id == "auto_session"
