"""API 모듈 테스트 (sales, invoice, etax, product, inventory)"""

import pytest
from unittest.mock import patch

from tests.conftest import make_success_response


class TestSalesAPI:

    def test_save_sale_builds_bulk_structure(self, client):
        ok_resp = make_success_response({"SuccessCnt": 1, "FailCnt": 0, "SlipNos": ["S001"]})
        with patch.object(client.session, "post", return_value=ok_resp) as mock_post:
            result = client.sales.save_sale([
                {"IO_DATE": "20260301", "WH_CD": "100", "PROD_CD": "90001", "QTY": "1"},
            ])
            assert result["Status"] == 200
            # POST 요청의 json body 검증
            call_kwargs = mock_post.call_args
            body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
            assert "SaleList" in body
            assert body["SaleList"][0]["Line"] == "0"
            assert body["SaleList"][0]["BulkDatas"]["PROD_CD"] == "90001"


class TestInvoiceAPI:

    def test_save_invoice_builds_structure(self, client):
        ok_resp = make_success_response({"SuccessCnt": 1, "FailCnt": 0})
        with patch.object(client.session, "post", return_value=ok_resp) as mock_post:
            result = client.invoice.save_invoice([
                {"TAX_GUBUN": "11", "CR_CODE": "4019", "SUPPLY_AMT": "100000"},
            ])
            assert result["Status"] == 200
            body = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")
            assert "InvoiceAutoList" in body
            assert body["InvoiceAutoList"][0]["BulkDatas"]["TAX_GUBUN"] == "11"


class TestETaxInvoiceAPI:

    def test_save_etax_builds_structure(self, client):
        ok_resp = make_success_response({"SuccessCnt": 1, "FailCnt": 0})
        with patch.object(client.session, "post", return_value=ok_resp) as mock_post:
            result = client.etax.save([
                {
                    "ISSUE_TYPE": "01",
                    "TAX_INVOICE_TYPE": "01",
                    "IO_DATE": "20260317",
                    "CUST_CD": "C001",
                    "SUPPLY_AMT": "100000",
                    "TAX_AMT": "10000",
                    "TOTAL_AMT": "110000",
                },
            ])
            assert result["Status"] == 200
            body = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")
            assert "ETaxInvoiceList" in body
            assert body["ETaxInvoiceList"][0]["BulkDatas"]["ISSUE_TYPE"] == "01"

    def test_cancel_etax(self, client):
        ok_resp = make_success_response({"SuccessCnt": 1, "FailCnt": 0})
        with patch.object(client.session, "post", return_value=ok_resp):
            result = client.etax.cancel([
                {"SLIP_NO": "12345", "IO_DATE": "20260317", "REMARKS": "취소"},
            ])
            assert result["Status"] == 200


class TestProductAPI:

    def test_get_list_no_filter(self, client):
        ok_resp = make_success_response({"Result": [{"PROD_CD": "90001"}]})
        with patch.object(client.session, "post", return_value=ok_resp):
            result = client.product.get_list()
            assert result["Status"] == 200

    def test_get_list_with_filter(self, client):
        ok_resp = make_success_response({"Result": []})
        with patch.object(client.session, "post", return_value=ok_resp) as mock_post:
            client.product.get_list(prod_cd="90001")
            body = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")
            assert body["PROD_CD"] == "90001"


class TestInventoryAPI:

    def test_get_product_list(self, client):
        ok_resp = make_success_response({"Result": []})
        with patch.object(client.session, "post", return_value=ok_resp):
            result = client.inventory.get_product_list()
            assert result["Status"] == 200
