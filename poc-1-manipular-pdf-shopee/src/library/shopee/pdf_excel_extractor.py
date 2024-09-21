from io import BytesIO
from typing import List, Optional
import pandas as pd
import re

from library.shopee.pdf_content.pdf_content_name import PdfContentName, ContentNameType
from library.shopee.pdf_content.pdf_content_order_code import PdfContentOrderCode
from library.shopee.pdf_content.pdf_content_quantity import PdfContentQuantity
from library.shopee.pdf_content.pdf_content_variation_name import PdfContentVariationName
from library.shopee.pdf_content.pdf_content import PdfContent


class PdfExcelExtractor:
    __PATTERN_TO_SPLIT_PRODUCT_INFO = r'(?=\[\d+\])'

    def __init__(self, content_name_type: ContentNameType, excel_file_path: str | BytesIO):
        self.__pdf_contents: List[PdfContent] = self.__populate_pdf_contents(content_name_type, excel_file_path)

    def __populate_pdf_contents(self, content_name_type: ContentNameType,
                                excel_file_path: str) -> List[PdfContent]:
        __pdf_contents: List[PdfContent] = []
        for _, row in pd.read_excel(excel_file_path).iterrows():
            order_sn: str = row['order_sn']
            product_infos: str = row['product_info']

            products = [part.strip() for part in re.split(self.__PATTERN_TO_SPLIT_PRODUCT_INFO, product_infos) if
                        part.strip()]

            for product in products:
                __pdf_contents.append(PdfContent(
                    content_order_code=PdfContentOrderCode(order_sn),
                    content_name=PdfContentName(content_name_type, product),
                    variation_name=PdfContentVariationName(product),
                    quantity=PdfContentQuantity(product)
                ))

        return __pdf_contents

    def list_pdf_contents_by_order_code(self, order_code: Optional[str]) -> List[PdfContent]:
        return [item for item in self.__pdf_contents if item.content_order_code.text_value == order_code]
