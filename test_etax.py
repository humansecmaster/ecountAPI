"""전자세금계산서 발급 API 테스트"""

import os
import json
from dotenv import load_dotenv
from ecount import EcountClient

load_dotenv()

client = EcountClient(
    zone=os.environ["ECOUNT_ZONE"],
    com_code=os.environ["ECOUNT_COM_CODE"],
    user_id=os.environ["ECOUNT_USER_ID"],
    api_cert_key=os.environ["ECOUNT_API_CERT_KEY"],
)

session_id = client.login()
print(f"로그인 성공 - SESSION_ID: {session_id[:20]}...")

# ── 1. 과세 매출 전자세금계산서 (정발행) ──────────────────────
print("\n" + "=" * 60)
print("[테스트 1] 과세 매출 전자세금계산서 정발행")
print("=" * 60)
try:
    result = client.etax.save([
        {
            "ISSUE_TYPE": "01",           # 정발행
            "TAX_INVOICE_TYPE": "01",     # 세금계산서
            "IO_DATE": "20260317",        # 작성일자
            "CUST_CD": "AU1100-1",        # 거래처코드
            "SUPPLY_TYPE": "01",          # 과세
            "SUPPLY_AMT": "100000",       # 공급가액
            "TAX_AMT": "10000",           # 세액
            "TOTAL_AMT": "110000",        # 합계
            "REMARKS": "API 전자세금계산서 발급 테스트",
            "Items": [
                {
                    "PROD_CD": "",
                    "PROD_DES": "테스트 품목",
                    "QTY": "1",
                    "UNIT_PRICE": "100000",
                    "SUPPLY_AMT": "100000",
                    "TAX_AMT": "10000",
                }
            ],
        }
    ])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    data = result.get("Data", {})
    print(f"\n  결과: 성공 {data.get('SuccessCnt', 0)}건 / 실패 {data.get('FailCnt', 0)}건")
except Exception as e:
    print(f"  오류: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("테스트 완료")
print("=" * 60)
