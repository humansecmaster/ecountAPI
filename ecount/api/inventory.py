"""재고 관련 API"""

from .base import BaseAPI


class InventoryAPI(BaseAPI):
    """재고 조회 API"""

    def get_product_list(self, prod_cd: str | None = None) -> dict:
        """품목별 재고/기본정보 목록 조회

        Args:
            prod_cd: 품목코드 필터 (없으면 전체)

        Returns:
            품목 기본정보 목록 (Data.Result 배열)
        """
        data = {}
        if prod_cd:
            data["PROD_CD"] = prod_cd
        return self.post("/InventoryBasic/GetBasicProductsList", data=data)
