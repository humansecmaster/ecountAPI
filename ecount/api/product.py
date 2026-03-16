"""품목 관련 API"""

from .base import BaseAPI


class ProductAPI(BaseAPI):
    """품목 관리 API"""

    def get_list(self, prod_cd: str | None = None, prod_nm: str | None = None) -> dict:
        """품목 기본정보 목록 조회

        Args:
            prod_cd: 품목코드 (부분 검색 가능)
            prod_nm: 품목명 (부분 검색 가능)

        Returns:
            품목 목록 (Data.Result 배열)
        """
        data = {}
        if prod_cd:
            data["PROD_CD"] = prod_cd
        if prod_nm:
            data["PROD_DES"] = prod_nm
        return self.post("/InventoryBasic/GetBasicProductsList", data=data)
