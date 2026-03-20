"""세금계산서(회계전표) API 직접 연동 테스트"""

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
print(f"API Base URL: {client.auth.base_url}")

# ── 1. 과세매출 세금계산서 등록 테스트 ──────────────────────────
print("\n" + "=" * 60)
print("[테스트 1] 과세매출 세금계산서 (TAX_GUBUN=11)")
print("=" * 60)
try:
    result = client.invoice.save_invoice([
        {
            "TAX_GUBUN": "11",        # 과세매출
            "CR_CODE": "4019",         # 매출계정코드
            "SUPPLY_AMT": "100000",    # 공급가액 10만원
            "VAT_AMT": "10000",        # 부가세 1만원
            "TRX_DATE": "20260317",    # 오늘 날짜
            "REMARKS": "API 테스트 - 과세매출 세금계산서",
        }
    ])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    data = result.get("Data", {})
    print(f"\n  결과: 성공 {data.get('SuccessCnt', 0)}건 / 실패 {data.get('FailCnt', 0)}건")
    if data.get("SlipNos"):
        print(f"  전표번호: {data['SlipNos']}")
except Exception as e:
    print(f"  오류: {e}")

# ── 2. 거래처 지정 과세매출 세금계산서 ─────────────────────────
print("\n" + "=" * 60)
print("[테스트 2] 거래처 지정 과세매출 세금계산서")
print("=" * 60)
try:
    result = client.invoice.save_invoice([
        {
            "TAX_GUBUN": "11",
            "CR_CODE": "4019",
            "CUST": "TEST001",
            "CUST_DES": "테스트거래처",
            "SUPPLY_AMT": "200000",
            "VAT_AMT": "20000",
            "TRX_DATE": "20260317",
            "REMARKS": "거래처 지정 테스트",
        }
    ])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    data = result.get("Data", {})
    print(f"\n  결과: 성공 {data.get('SuccessCnt', 0)}건 / 실패 {data.get('FailCnt', 0)}건")
except Exception as e:
    print(f"  오류: {e}")

# ── 3. 과세매입 세금계산서 테스트 ──────────────────────────────
print("\n" + "=" * 60)
print("[테스트 3] 과세매입 세금계산서 (TAX_GUBUN=21)")
print("=" * 60)
try:
    result = client.invoice.save_invoice([
        {
            "TAX_GUBUN": "21",        # 과세매입
            "DR_CODE": "1469",         # 매입계정코드
            "SUPPLY_AMT": "500000",    # 공급가액 50만원
            "VAT_AMT": "50000",        # 부가세 5만원
            "TRX_DATE": "20260317",
            "REMARKS": "API 테스트 - 과세매입 세금계산서",
        }
    ])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    data = result.get("Data", {})
    print(f"\n  결과: 성공 {data.get('SuccessCnt', 0)}건 / 실패 {data.get('FailCnt', 0)}건")
except Exception as e:
    print(f"  오류: {e}")

# ── 4. 복수 건 동시 등록 테스트 ────────────────────────────────
print("\n" + "=" * 60)
print("[테스트 4] 복수 건 동시 등록 (과세매출 2건)")
print("=" * 60)
try:
    result = client.invoice.save_invoice([
        {
            "TAX_GUBUN": "11",
            "CR_CODE": "4019",
            "SUPPLY_AMT": "150000",
            "VAT_AMT": "15000",
            "TRX_DATE": "20260317",
            "REMARKS": "복수건 테스트 1",
        },
        {
            "TAX_GUBUN": "11",
            "CR_CODE": "4019",
            "SUPPLY_AMT": "250000",
            "VAT_AMT": "25000",
            "TRX_DATE": "20260317",
            "REMARKS": "복수건 테스트 2",
        },
    ])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    data = result.get("Data", {})
    print(f"\n  결과: 성공 {data.get('SuccessCnt', 0)}건 / 실패 {data.get('FailCnt', 0)}건")
except Exception as e:
    print(f"  오류: {e}")

print("\n" + "=" * 60)
print("테스트 완료")
print("=" * 60)
