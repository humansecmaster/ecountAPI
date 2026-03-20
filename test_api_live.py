"""ECOUNT Open API 라이브 테스트 (테스트 인증키 사용)

테스트 URL: http://sboapi{zone}.ecount.com
테스트 결과 (2026-03-18):
  - 로그인: 성공
  - 품목 목록 조회: 성공 (196건)
  - 매출 등록 (Sale/SaveSale): 성공
  - 견적서 등록 (Quotation/SaveQuotation): 성공
  - 회계전표 (InvoiceAuto/SaveInvoiceAuto): API 존재, 회계 거래처 미등록으로 실패
  - 전자세금계산서 (ETaxInvoice): 엔드포인트 미제공
  - 거래처 등록 (BasicCust): 테스트 서버 미지원
  - 거래명세서: Open API 미제공
"""

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
    test_mode=True,
)


def pp(label, result):
    print(f"\n{'=' * 60}")
    print(f"[{label}]")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    data = result.get("Data", {})
    if "SuccessCnt" in data:
        print(f"\n  -> 성공 {data['SuccessCnt']}건 / 실패 {data['FailCnt']}건")


# ── 1. 로그인 ────────────────────────────────────────────
print("=" * 60)
print("[1] 로그인")
print("=" * 60)
try:
    session_id = client.login()
    print(f"성공 - SESSION_ID: {session_id[:20]}...")
    print(f"Base URL: {client.auth.base_url}")
except Exception as e:
    print(f"실패: {type(e).__name__}: {e}")
    exit(1)

# ── 2. 매출 등록 ─────────────────────────────────────────
try:
    result = client.sales.save_sale([{
        "IO_DATE": "20260318",
        "WH_CD": "100",
        "PROD_CD": "90001",
        "QTY": "1",
        "UNIT_PRICE": "50000",
    }])
    pp("매출 등록", result)
except Exception as e:
    print(f"\n매출 등록 오류: {type(e).__name__}: {e}")

# ── 3. 회계전표 (매출매입전표 II 자동분개) ────────────────
try:
    result = client.invoice.save_invoice([{
        "TAX_GUBUN": "11",
        "CR_CODE": "4019",
        "CUST": "AU1100-1",
        "SUPPLY_AMT": "100000",
        "VAT_AMT": "10000",
        "TRX_DATE": "20260318",
        "REMARKS": "API 테스트 - 과세매출 세금계산서",
    }])
    pp("회계전표 (과세매출)", result)
except Exception as e:
    print(f"\n회계전표 오류: {type(e).__name__}: {e}")

# ── 4. 전자세금계산서 (엔드포인트 미제공 확인) ────────────
print(f"\n{'=' * 60}")
print("[전자세금계산서] ECOUNT Open API 미제공 (2026-03 기준)")
print("  - /ETaxInvoice/SaveETaxInvoice -> Not Found")
print("  - 대안: InvoiceAuto/SaveInvoiceAuto (매출매입전표)")
print("=" * 60)

# ── 5. 거래명세서 ────────────────────────────────────────
print(f"\n{'=' * 60}")
print("[거래명세서] ECOUNT Open API 미제공 (2026-03 기준)")
print("  - 전용 엔드포인트 없음")
print("  - ECOUNT: '추가 모듈은 고객 피드백에 따라 계속 추가 예정'")
print("=" * 60)

print("\n테스트 완료")
