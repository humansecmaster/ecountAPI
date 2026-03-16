"""거래처 관련 API (현재 이카운트 OAPI에서 거래처 조회 엔드포인트는 공식 API 문서 확인 필요)"""

from .base import BaseAPI


class CustomerAPI(BaseAPI):
    """거래처 관리 API

    Note:
        거래처 조회/등록 API 경로는 공식 이카운트 API 포털에서 확인이 필요합니다.
        https://sboapi.ecount.com/ECERP/OAPI/OAPIView?lan_type=ko-KR
    """
    pass
