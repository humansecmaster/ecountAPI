"""이카운트 API 전송 제한(Rate Limit) 관리

ECOUNT OAPI 전송 기준:
  - 로그인: 1회 / 10초
  - 입력/조회 API (벌크): 1회 / 10초
  - 단건 조회 API: 1회 / 1초
"""

import time
import threading


# 카테고리별 최소 간격 (초)
DEFAULT_INTERVALS: dict[str, float] = {
    "login": 10.0,
    "bulk": 10.0,
    "query_single": 1.0,
}


class RateLimiter:
    """카테고리별 API 호출 간격을 제어합니다.

    동일 카테고리의 API를 연속 호출할 때,
    ECOUNT 전송 기준에 맞춰 자동으로 대기합니다.
    """

    def __init__(self, intervals: dict[str, float] | None = None):
        self._intervals = intervals or DEFAULT_INTERVALS.copy()
        self._last_call: dict[str, float] = {}
        self._lock = threading.Lock()

    def wait(self, category: str) -> float:
        """필요 시 대기한 뒤, 실제 대기한 시간(초)을 반환합니다.

        Args:
            category: API 카테고리 ("login", "bulk", "query_single")

        Returns:
            실제 대기한 시간 (초). 대기 불필요 시 0.0
        """
        interval = self._intervals.get(category, 10.0)

        with self._lock:
            now = time.monotonic()
            last = self._last_call.get(category, 0.0)
            elapsed = now - last
            wait_time = max(0.0, interval - elapsed)

        if wait_time > 0:
            time.sleep(wait_time)

        with self._lock:
            self._last_call[category] = time.monotonic()

        return wait_time
