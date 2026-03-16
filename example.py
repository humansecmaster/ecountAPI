"""이카운트 오픈 API 연동 예제"""

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

# ── 품목 목록 조회 ─────────────────────────────────────────────
print("\n[품목 목록 조회]")
result = client.product.get_list()
items = result.get("Data", {}).get("Result", [])
print(f"총 {len(items)}개 품목")
for item in items[:3]:
    print(f"  [{item.get('PROD_CD')}] {item.get('PROD_DES')} / 판매단가: {item.get('OUT_PRICE')}")

# 첫 번째 품목코드를 판매 등록에 활용
first_prod = items[0] if items else None

# ── 판매 등록 ──────────────────────────────────────────────────
print("\n[판매 등록]")
if first_prod:
    result = client.sales.save_sale([
        {
            "IO_DATE":    "20260301",
            "WH_CD":      "100",
            "PROD_CD":    first_prod["PROD_CD"],
            "PROD_DES":   first_prod["PROD_DES"],
            "QTY":        "1",
            "UNIT_PRICE": "10000",
        }
    ])
    sc = result.get("Data", {}).get("SuccessCnt", 0)
    fc = result.get("Data", {}).get("FailCnt", 0)
    slip_nos = result.get("Data", {}).get("SlipNos", [])
    print(f"  성공: {sc}건 / 실패: {fc}건")
    if slip_nos:
        print(f"  전표번호: {slip_nos}")
    if fc:
        errs = result.get("Errors") or []
        for e in errs:
            print(f"  오류: {e.get('Message','')}")
else:
    print("  등록 가능한 품목 없음")

# ── 복수 품목 판매 등록 예제 ───────────────────────────────────
# print("\n[복수 품목 판매 등록]")
# result = client.sales.save_sale([
#     {"IO_DATE": "20260301", "WH_CD": "100", "PROD_CD": "90001", "PROD_DES": "품목1", "QTY": "2", "UNIT_PRICE": "50000"},
#     {"IO_DATE": "20260301", "WH_CD": "100", "PROD_CD": "90002", "PROD_DES": "품목2", "QTY": "1", "UNIT_PRICE": "30000"},
# ])
# print(json.dumps(result, ensure_ascii=False, indent=2))
