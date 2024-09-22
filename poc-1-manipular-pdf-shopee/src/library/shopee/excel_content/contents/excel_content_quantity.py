from reportlab.lib.enums import TA_RIGHT

from library.shopee.excel_content.base.excel_content import ExcelContent
from library.shopee.pdf_style.pdf_paragraph_style import PdfParagraphStyle
import re


class ExcelContentQuantity(ExcelContent):
    __PATTERN_TO_FIND_QUANTITY = r"Quantity:(.*?);"

    def __init__(self, style: PdfParagraphStyle, excel_content_product: str):
        value = self.__extract_quantity(excel_content_product)
        super().__init__(value=value, style=self.__get_style(style=style, value=value))

    def __extract_quantity(self, excel_content_product: str) -> str:
        match_result = re.search(self.__PATTERN_TO_FIND_QUANTITY, excel_content_product)
        if match_result:
            return match_result.group(1)
        else:
            raise Exception("Não encontrado a correspodência para 'Quantity:' no excel informado")

    @staticmethod
    def __get_style(style: PdfParagraphStyle, value: str) -> PdfParagraphStyle:
        parsed_value: int = int(value)
        font_size = style.default_font_size() + 3 if parsed_value > 1 else style.default_font_size()
        leading = style.default_leading() + 3 if parsed_value > 1 else style.default_leading()
        return PdfParagraphStyle(font_size=font_size, leading=leading, alignment=TA_RIGHT)
