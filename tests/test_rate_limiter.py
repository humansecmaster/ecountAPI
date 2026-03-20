"""Rate Limiter 테스트"""

import time
import pytest

from ecount.rate_limiter import RateLimiter


class TestRateLimiter:

    def test_first_call_no_wait(self):
        limiter = RateLimiter(intervals={"bulk": 1.0})
        waited = limiter.wait("bulk")
        assert waited == 0.0

    def test_second_call_waits(self):
        limiter = RateLimiter(intervals={"bulk": 0.2})
        limiter.wait("bulk")
        start = time.monotonic()
        limiter.wait("bulk")
        elapsed = time.monotonic() - start
        assert elapsed >= 0.15  # 약간의 오차 허용

    def test_different_categories_independent(self):
        limiter = RateLimiter(intervals={"bulk": 10.0, "query_single": 1.0})
        limiter.wait("bulk")
        # query_single은 bulk과 독립이므로 즉시 실행
        waited = limiter.wait("query_single")
        assert waited == 0.0

    def test_unknown_category_uses_default_interval(self):
        limiter = RateLimiter(intervals={"bulk": 0.1})
        # 존재하지 않는 카테고리는 기본 10초 간격
        waited = limiter.wait("unknown")
        assert waited == 0.0  # 첫 호출은 대기 없음
