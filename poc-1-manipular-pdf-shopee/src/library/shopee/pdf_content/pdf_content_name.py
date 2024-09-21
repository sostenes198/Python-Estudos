from enum import Enum, auto
import re
from library.shopee.pdf_content.base.pdf_content import PdfContent
from library.shopee.pdf_style.pdf_paragraph_style import PdfParagraphStyle


class ContentNameType(Enum):
    SKU = auto()
    PRODUCT_NAME = auto()


class PdfContentName(PdfContent):
    __PATTERN_TO_FIND_SKU_REFERENCE: str = r"SKU Reference No\.:(.*?);"
    __PATTERN_TO_FIND_PRODUCT_NAME: str = r"Product Name:(.*?);"

    def __init__(self, content_name_type: ContentNameType, excel_content_product: str):
        value = self.__extract_name(content_name_type, excel_content_product)
        super().__init__(value, PdfParagraphStyle())

    def __extract_name(self, content_name_type: ContentNameType, excel_content_product: str) -> str:
        match content_name_type:
            case ContentNameType.PRODUCT_NAME:
                return self.__extract_name_from_product_name(excel_content_product)
            case ContentNameType.SKU:
                return self.__extract_name_from_sku(excel_content_product)
            case _:
                return self.__extract_name_from_sku(excel_content_product)

    def __extract_name_from_sku(self, excel_content_product: str) -> str:
        match_result = re.search(self.__PATTERN_TO_FIND_SKU_REFERENCE, excel_content_product)
        if match_result:
            return match_result.group(1)
        else:
            raise Exception("Não encontrado a correspodência para 'SKU Reference No.:' no excel informado")

    def __extract_name_from_product_name(self, excel_content_product: str) -> str:
        match_result = re.search(self.__PATTERN_TO_FIND_PRODUCT_NAME, excel_content_product)
        if match_result:
            return match_result.group(1)
        else:
            raise Exception("Não encontrado a correspodência para 'Product Name:' no excel informado")
