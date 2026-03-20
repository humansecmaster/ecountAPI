"""회계 전표(세금계산서) 관련 API"""

from .base import BaseAPI


class InvoiceAPI(BaseAPI):
    """매출·매입전표 II 자동분개 API

    ECOUNT 회계 전표(세금계산서)를 등록합니다.

    TAX_GUBUN 코드:
        11: 과세매출, 12: 영세매출, 13: 면세매출
        21: 과세매입, 22: 영세매입, 23: 면세매입
        14: 신용카드매출, 24: 신용카드매입

    실제 요청 구조:
        POST /InvoiceAuto/SaveInvoiceAuto?SESSION_ID=...
        {
            "InvoiceAutoList": [
                {
                    "BulkDatas": {
                        "TAX_GUBUN": "11",
                        "CR_CODE": "4019",
                        "SUPPLY_AMT": "100000",
                        "VAT_AMT": "10000",
                        ...
                    }
                }
            ]
        }
    """

    def save_invoice(self, items: list[dict]) -> dict:
        """세금계산서(회계전표) 등록 - 매출매입전표 II 자동분개

        Args:
            items: 전표 리스트. 각 항목:
                - TAX_GUBUN (str): 매출/매입 구분 (필수). 11=과세매출, 21=과세매입 등
                - CR_CODE   (str): 매출계정코드 (매출시 필수). 예: "4019"
                - DR_CODE   (str): 매입계정코드 (매입시 필수). 예: "1469"
                - CUST      (str): 거래처코드 (선택)
                - CUST_DES  (str): 거래처명 (선택)
                - SUPPLY_AMT(str): 공급가액 (선택)
                - VAT_AMT   (str): 부가세 (선택)
                - TRX_DATE  (str): 전표일자 YYYYMMDD (선택, 생략시 오늘)
                - REMARKS   (str): 적요 (선택)
                - SITE_CD   (str): 부서코드 (선택)
                - PJT_CD    (str): 프로젝트코드 (선택)

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
        """
        bulk_list = [
            {"BulkDatas": item}
            for item in items
        ]
        return self.post(
            "/InvoiceAuto/SaveInvoiceAuto",
            data={"InvoiceAutoList": bulk_list},
        )
