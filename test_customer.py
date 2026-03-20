"""거래처 등록 테스트"""
import requests
import json

# 1. Zone 조회
resp = requests.post('https://oapi.ecount.com/OAPI/V2/Zone', json={'COM_CODE': '157845'})
zone = resp.json()['Data']['ZONE']
print(f'ZONE: {zone}')

# 2. 로그인 (테스트 서버)
resp = requests.post(f'https://sboapi{zone.lower()}.ecount.com/OAPI/V2/OAPILogin', json={
    'COM_CODE': '157845', 'USER_ID': 'HUMANSEC',
    'API_CERT_KEY': '34f8e3ccde50c4862876dd92d77e42f538',
    'LAN_TYPE': 'ko-KR', 'ZONE': zone,
})
login = resp.json()
sid = login['Data']['Datas']['SESSION_ID']
host = login['Data']['Datas']['HOST_URL']
base = f'https://{host}'
print(f'SESSION: {sid}')
print(f'HOST: {host}')

# 3. 거래처 등록 시도
print('\n=== 거래처 등록: /OAPI/V2/AccountBasic/SaveBasicCust ===')
body = {'CustList': [{'BulkDatas': {'BUSINESS_NO': 'TEST001', 'CUST_NAME': '테스트거래처', 'BOSS_NAME': '홍길동'}}]}
resp = requests.post(f'{base}/OAPI/V2/AccountBasic/SaveBasicCust', params={'SESSION_ID': sid}, json=body)
print(f'Status: {resp.status_code}')
print(json.dumps(resp.json(), ensure_ascii=False, indent=2))

# 4. 품목등록 (비교용 - 정상 동작 확인)
print('\n=== 품목 등록 (비교용): /OAPI/V2/BasicProduct/SaveBasicProduct ===')
body2 = {'ProductList': [{'BulkDatas': {'PROD_CD': 'TESTPRD999', 'PROD_DES': '테스트품목'}}]}
resp2 = requests.post(f'{base}/OAPI/V2/BasicProduct/SaveBasicProduct', params={'SESSION_ID': sid}, json=body2)
print(f'Status: {resp2.status_code}')
print(json.dumps(resp2.json(), ensure_ascii=False, indent=2))
