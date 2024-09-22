import re
from io import BytesIO
from typing import List, Optional

import pandas as pd

from library.shopee.excel_content.contents.excel_content_name import ExcelContentName
from library.shopee.excel_content.contents.excel_content_order_code import ExcelContentOrderCode
from library.shopee.excel_content.contents.excel_content_quantity import ExcelContentQuantity
from library.shopee.excel_content.contents.excel_content_variation_name import ExcelContentVariationName
from library.shopee.excel_content.excel_content_manager import ExcelContentManager
from library.shopee.pdf_style.pdf_paragraph_style import PdfParagraphStyle
from library.shopee.shopee_config import ShopeeExcelConfig


class ExcelShopeeExtractor:
    __PATTERN_TO_SPLIT_PRODUCT_INFO = r'(?=\[\d+\])'

    def __init__(self, config: ShopeeExcelConfig, excel_file_path_or_stream: str | BytesIO):
        self.__pdf_contents: List[ExcelContentManager] = self.__populate_pdf_contents(config=config,
                                                                                      excel_file_path=excel_file_path_or_stream)

    def list_pdf_contents_by_order_code(self, order_code: Optional[str]) -> List[ExcelContentManager]:
        return [item for item in self.__pdf_contents if item.content_order_code.text_value == order_code]

    def __populate_pdf_contents(self, config: ShopeeExcelConfig,
                                excel_file_path: str | BytesIO) -> List[ExcelContentManager]:
        pdf_contents: List[ExcelContentManager] = []
        default_paragraph_style: PdfParagraphStyle = PdfParagraphStyle(font_size=config.font_size)

        for _, row in pd.read_excel(excel_file_path).iterrows():
            order_sn: str = row['order_sn']
            product_infos: str = row['product_info']

            products = [part.strip() for part in re.split(self.__PATTERN_TO_SPLIT_PRODUCT_INFO, product_infos) if
                        part.strip()]

            for product in products:
                pdf_contents.append(ExcelContentManager(
                    content_order_code=ExcelContentOrderCode(style=default_paragraph_style,
                                                             excel_content_order_sn=order_sn),
                    content_name=ExcelContentName(style=default_paragraph_style,
                                                  content_name_type=config.content_name_type,
                                                  excel_content_product=product),
                    variation_name=ExcelContentVariationName(style=default_paragraph_style,
                                                             excel_content_product=product),
                    quantity=ExcelContentQuantity(style=default_paragraph_style, excel_content_product=product)
                ))

        return pdf_contents
