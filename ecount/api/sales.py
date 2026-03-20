"""판매 관련 API"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..client import EcountClient

from .base import BaseAPI


class SalesAPI(BaseAPI):
    """판매 처리 API

    실제 요청 구조 (테스트 확인):
        POST /Sale/SaveSale?SESSION_ID=...
        {
            "SaleList": [
                {
                    "Line": "0",
                    "BulkDatas": {
                        "SESSION_ID": "...",
                        "IO_DATE": "20260228",
                        "WH_CD": "100",
                        "PROD_CD": "90001",
                        "PROD_DES": "품목명",
                        "QTY": "1",
                        "UNIT_PRICE": "10000",
                        "PRICE": "10000"
                    }
                }
            ]
        }
    """

    def save_sale(self, items: list[dict]) -> dict:
        """판매 등록 (복수 품목 지원)

        Args:
            items: 판매 품목 리스트. 각 항목:
                - IO_DATE (str): 판매일자 YYYYMMDD (필수)
                - WH_CD   (str): 창고코드 (필수)
                - PROD_CD (str): 품목코드 (필수)
                - PROD_DES(str): 품목명
                - QTY     (str): 수량 (필수)
                - UNIT_PRICE(str): 단가
                - PRICE   (str): 단가 (UNIT_PRICE와 함께 입력해야 반영됨)
                - SUPPLY_AMT(str): 공급가액 (선택)
                - VAT_AMT(str): 부가세 (선택)
                - SIZE_DES(str): 규격 (선택)
                - CUST    (str): 거래처코드 (선택, CUST_CD 아님 주의)

        Returns:
            {
                "Data": {
                    "SuccessCnt": 1,
                    "FailCnt": 0,
                    "SlipNos": ["전표번호"],
                    "ResultDetails": [{"Line": 0, "IsSuccess": true, ...}]
                },
                "Status": "200"
            }

        Example:
            result = client.sales.save_sale([
                {
                    "IO_DATE": "20260301",
                    "WH_CD": "100",
                    "PROD_CD": "90001",
                    "PROD_DES": "ST45L -BZ -2",
                    "QTY": "2",
                    "UNIT_PRICE": "50000",
                    "PRICE": "50000",
                }
            ])
        """
        session_id = self._client.auth.session_id
        bulk_list = [
            {"Line": str(i), "BulkDatas": {"SESSION_ID": session_id, **item}}
            for i, item in enumerate(items)
        ]
        return self.post("/Sale/SaveSale", data={"SaleList": bulk_list})
