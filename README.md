# 이카운트 오픈 API Python 연동

이카운트(ECOUNT) ERP 오픈 API를 Python으로 쉽게 연동하기 위한 클라이언트 라이브러리입니다.

## 지원 기능

| 모듈 | 기능 |
|------|------|
| `client.inventory` | 재고 조회/입출고 |
| `client.sales` | 판매주문, 판매, 견적 |
| `client.purchase` | 구매주문, 구매, 생산 |
| `client.product` | 품목 조회/등록/수정/삭제 |
| `client.customer` | 거래처 조회/등록/수정/삭제 |

## 설치

```bash
pip install -r requirements.txt
```

## 초기 설정

1. `.env.example`을 복사해 `.env` 파일 생성

```bash
cp .env.example .env
```

2. `.env` 파일에 이카운트 정보 입력

```env
ECOUNT_ZONE=1
ECOUNT_COM_CODE=회사코드
ECOUNT_USER_ID=사용자ID
ECOUNT_API_CERT_KEY=API인증키
```

> API 인증키 발급: 이카운트 ERP 로그인 → **사용자 맞춤설정 > 정보 > API 인증키 발급**

## 사용 예제

```python
from dotenv import load_dotenv
import os
from ecount import EcountClient

load_dotenv()

client = EcountClient(
    zone=os.environ["ECOUNT_ZONE"],
    com_code=os.environ["ECOUNT_COM_CODE"],
    user_id=os.environ["ECOUNT_USER_ID"],
    api_cert_key=os.environ["ECOUNT_API_CERT_KEY"],
)

client.login()

# 재고 잔액 조회
stock = client.inventory.get_stock_balance()

# 판매주문 등록
client.sales.save_order({
    "CUST_CD": "C001",
    "IO_DATE": "20250301",
    "Items": [
        {"PROD_CD": "P001", "QTY": 10, "UNIT_PRICE": 5000},
    ]
})

# 품목 목록 조회
products = client.product.get_list(prod_nm="노트북")

# 거래처 등록
client.customer.save({
    "CUST_CD": "C001",
    "CUST_NM": "테스트 고객사",
    "CUST_TYPE": "C",
})
```

더 많은 예제는 `example.py`를 참고하세요.

## 프로젝트 구조

```
ecount/
├── ecount/
│   ├── __init__.py
│   ├── client.py       # 메인 클라이언트
│   ├── auth.py         # 세션키 인증
│   └── api/
│       ├── base.py     # 베이스 API 클래스
│       ├── inventory.py
│       ├── sales.py
│       ├── purchase.py
│       ├── product.py
│       └── customer.py
├── example.py
├── requirements.txt
└── .env.example
```

## 참고

- [이카운트 오픈 API 공식 포털](https://sboapi.ecount.com/ECERP/OAPI/OAPIView?lan_type=ko-KR)
- API 인증키 유효 기간: 만료 3개월 전에 갱신 필요
