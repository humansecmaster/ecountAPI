"""전자세금계산서 발급 API

NOTE: 2026-03 기준 ECOUNT Open API에서 전자세금계산서 전용 엔드포인트
      (/ETaxInvoice/SaveETaxInvoice 등)는 제공되지 않습니다.
      아래 코드는 향후 API 추가 시를 대비한 구현입니다.
      현재는 InvoiceAuto/SaveInvoiceAuto (매출매입전표 II 자동분개)를
      대안으로 사용하세요.
"""

from .base import BaseAPI


class ETaxInvoiceAPI(BaseAPI):
    """전자세금계산서 발급 API (현재 미지원)

    WARNING: 2026-03 기준 ECOUNT Open API에 해당 엔드포인트가 없습니다.
    향후 추가될 경우를 대비한 구현입니다.

    ECOUNT ERP에서 전자세금계산서를 발급합니다.
    매출 전자세금계산서(정발행)와 매입 전자세금계산서(역발행)을 지원합니다.

    TAX_INVOICE_TYPE 코드:
        01: 세금계산서
        02: 수정세금계산서
        03: 계산서 (면세)
        04: 수정계산서 (면세)

    SUPPLY_TYPE 코드:
        01: 과세
        02: 영세
        03: 면세

    실제 요청 구조:
        POST /ETaxInvoice/SaveETaxInvoice?SESSION_ID=...
        {
            "ETaxInvoiceList": [
                {
                    "BulkDatas": {
                        "ISSUE_TYPE": "01",
                        "TAX_INVOICE_TYPE": "01",
                        "IO_DATE": "20260317",
                        "CUST_CD": "거래처코드",
                        ...
                        "Items": [
                            {"PROD_CD": "품목코드", "QTY": "1", ...}
                        ]
                    }
                }
            ]
        }
    """

    def save(self, invoices: list[dict]) -> dict:
        """전자세금계산서 발급

        Args:
            invoices: 전자세금계산서 리스트. 각 항목:
                - ISSUE_TYPE       (str): 발행유형. "01"=정발행, "02"=역발행 (필수)
                - TAX_INVOICE_TYPE (str): 세금계산서유형. "01"=세금계산서, "02"=수정, "03"=계산서(면세) (필수)
                - IO_DATE          (str): 작성일자 YYYYMMDD (필수)
                - CUST_CD          (str): 거래처코드 (필수)
                - SUPPLY_TYPE      (str): 과세유형. "01"=과세, "02"=영세, "03"=면세 (기본: "01")
                - SUPPLY_AMT       (str): 공급가액 합계 (필수)
                - TAX_AMT          (str): 세액 합계 (필수)
                - TOTAL_AMT        (str): 합계금액 (필수)
                - REMARKS          (str): 비고 (선택)
                - EMAIL             (str): 발급 후 전송할 이메일 (선택)
                - SITE_CD          (str): 부서코드 (선택)
                - PJT_CD           (str): 프로젝트코드 (선택)
                - Items            (list): 품목 리스트 (선택)
                    - PROD_CD      (str): 품목코드
                    - PROD_DES     (str): 품목명
                    - QTY          (str): 수량
                    - UNIT_PRICE   (str): 단가
                    - SUPPLY_AMT   (str): 공급가액
                    - TAX_AMT      (str): 세액

        Returns:
            {
                "Data": {
                    "SuccessCnt": 1,
                    "FailCnt": 0,
                    "ResultDetails": [{"Line": 0, "IsSuccess": true, ...}]
                },
                "Status": "200"
            }

        Example:
            result = client.etax.save([
                {
                    "ISSUE_TYPE": "01",
                    "TAX_INVOICE_TYPE": "01",
                    "IO_DATE": "20260317",
                    "CUST_CD": "C001",
                    "SUPPLY_AMT": "100000",
                    "TAX_AMT": "10000",
                    "TOTAL_AMT": "110000",
                    "REMARKS": "3월 거래분",
                    "Items": [
                        {
                            "PROD_CD": "90001",
                            "PROD_DES": "테스트 품목",
                            "QTY": "1",
                            "UNIT_PRICE": "100000",
                            "SUPPLY_AMT": "100000",
                            "TAX_AMT": "10000",
                        }
                    ],
                }
            ])
        """
        bulk_list = [
            {"BulkDatas": invoice}
            for invoice in invoices
        ]
        return self.post(
            "/ETaxInvoice/SaveETaxInvoice",
            data={"ETaxInvoiceList": bulk_list},
        )

    def cancel(self, invoices: list[dict]) -> dict:
        """전자세금계산서 발급 취소

        Args:
            invoices: 취소할 전자세금계산서 리스트. 각 항목:
                - SLIP_NO  (str): 전표번호 (필수)
                - IO_DATE  (str): 작성일자 YYYYMMDD (필수)
                - REMARKS  (str): 취소 사유 (선택)

        Returns:
            처리 결과
        """
        bulk_list = [
            {"BulkDatas": invoice}
            for invoice in invoices
        ]
        return self.post(
            "/ETaxInvoice/CancelETaxInvoice",
            data={"ETaxInvoiceList": bulk_list},
        )
