"""구매 관련 API"""

from .base import BaseAPI


class PurchaseAPI(BaseAPI):
    """구매 처리 API"""

    def save_purchase(self, purchase: dict) -> dict:
        """구매 등록

        Args:
            purchase: 구매 정보
                - IO_DATE: 구매일자 (YYYYMMDD)
                - CUST_CD: 거래처코드
                - WH_CD: 창고코드
                - Items: 품목 리스트
                    - PROD_CD: 품목코드
                    - PROD_DES: 품목명
                    - QTY: 수량
                    - UNIT_PRICE: 단가

        Returns:
            처리 결과
        """
        return self.post("/Purchases/SavePurchases", data=purchase)
