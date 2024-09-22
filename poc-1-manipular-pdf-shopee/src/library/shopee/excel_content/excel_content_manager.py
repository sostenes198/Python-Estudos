from library.shopee.excel_content.contents.excel_content_order_code import ExcelContentOrderCode
from library.shopee.excel_content.contents.excel_content_name import ExcelContentName
from library.shopee.excel_content.contents.excel_content_variation_name import ExcelContentVariationName
from library.shopee.excel_content.contents.excel_content_quantity import ExcelContentQuantity


class ExcelContentManager:
    def __init__(self, content_order_code: ExcelContentOrderCode, content_name: ExcelContentName,
                 variation_name: ExcelContentVariationName,
                 quantity: ExcelContentQuantity):
        self.__content_order_code: ExcelContentOrderCode = content_order_code
        self.__content_name: ExcelContentName = content_name
        self.__variation_name: ExcelContentVariationName = variation_name
        self.__quantity: ExcelContentQuantity = quantity

    @property
    def content_order_code(self) -> ExcelContentOrderCode:
        return self.__content_order_code

    @property
    def content_name(self) -> ExcelContentName:
        return self.__content_name

    @property
    def variation_name(self) -> ExcelContentVariationName:
        return self.__variation_name

    @property
    def quantity(self) -> ExcelContentQuantity:
        return self.__quantity
