"""에러 핸들링 테스트"""

import pytest
from unittest.mock import patch

from ecount import (
    EcountError,
    RateLimitError,
    SessionExpiredError,
    ValidationError,
    ServerError,
    NotFoundError,
)
from tests.conftest import make_success_response, make_error_response


class TestCheckResponse:
    """client._check_response 에러 분기 테스트"""

    def test_404_raises_not_found(self, client):
        resp = make_error_response(404)
        with pytest.raises(NotFoundError, match="존재하지 않는 API"):
            client._check_response(resp, "/Bad/Path")

    def test_412_raises_rate_limit(self, client):
        resp = make_error_response(412)
        with pytest.raises(RateLimitError, match="전송 횟수 기준 초과"):
            client._check_response(resp, "/Sale/SaveSale")

    def test_500_raises_server_error(self, client):
        resp = make_error_response(500, {"Message": "Internal Error"})
        with pytest.raises(ServerError):
            client._check_response(resp, "/Sale/SaveSale")

    def test_session_timeout_raises_session_expired(self, client):
        resp = make_error_response(200)
        resp.json.return_value = {
            "Status": 500,
            "Message": "Session Timeout",
        }
        with pytest.raises(SessionExpiredError, match="세션 만료"):
            client._check_response(resp, "/Sale/SaveSale")

    def test_validation_error_with_fields(self, client):
        resp = make_error_response(200)
        resp.json.return_value = {
            "Status": 500,
            "Errors": [
                {"Field": "PROD_CD", "Message": "품목코드 필수"},
                {"Field": "QTY", "Message": "수량 필수"},
            ],
        }
        with pytest.raises(ValidationError) as exc_info:
            client._check_response(resp, "/Sale/SaveSale")
        assert "PROD_CD" in exc_info.value.fields

    def test_partial_failure_raises_validation(self, client):
        resp = make_error_response(200)
        resp.json.return_value = {
            "Status": 200,
            "Data": {
                "SuccessCnt": 1,
                "FailCnt": 1,
                "ResultDetails": [
                    {"Line": 0, "IsSuccess": True},
                    {"Line": 1, "IsSuccess": False, "Message": "품목코드 없음"},
                ],
            },
        }
        with pytest.raises(ValidationError, match="입력 실패 1건"):
            client._check_response(resp, "/Sale/SaveSale")

    def test_success_returns_data(self, client):
        resp = make_success_response({"SuccessCnt": 1, "FailCnt": 0})
        result = client._check_response(resp, "/Sale/SaveSale")
        assert result["Status"] == 200


class TestAutoRetryOnSessionExpired:
    """세션 만료 시 자동 재로그인 테스트"""

    def test_post_retries_on_session_expired(self, client):
        expired_resp = make_error_response(200)
        expired_resp.json.return_value = {
            "Status": 500,
            "Message": "Session Timeout",
        }
        ok_resp = make_success_response({"SuccessCnt": 1, "FailCnt": 0})

        with patch.object(client.session, "post", side_effect=[expired_resp, ok_resp]):
            with patch.object(client.auth, "login", return_value="NEW_SESSION"):
                result = client.post("/Sale/SaveSale", data={})
                assert result["Status"] == 200

    def test_post_no_retry_when_disabled(self, client):
        client.auto_retry = False
        expired_resp = make_error_response(200)
        expired_resp.json.return_value = {
            "Status": 500,
            "Message": "Session Timeout",
        }

        with patch.object(client.session, "post", return_value=expired_resp):
            with pytest.raises(SessionExpiredError):
                client.post("/Sale/SaveSale", data={})
