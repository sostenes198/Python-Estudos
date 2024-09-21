from library.shopee.pdf_content.base.pdf_content import PdfContent
from library.shopee.pdf_style.pdf_paragraph_style import PdfParagraphStyle
import re


class PdfContentQuantity(PdfContent):
    __PATTERN_TO_FIND_QUANTITY = r"Quantity:(.*?);"

    def __init__(self, excel_content_product: str):
        value = self.__extract_quantity(excel_content_product)
        super().__init__(value, self.__get_style(value))

    def __extract_quantity(self, excel_content_product: str) -> str:
        match_result = re.search(self.__PATTERN_TO_FIND_QUANTITY, excel_content_product)
        if match_result:
            return match_result.group(1)
        else:
            raise Exception("Não encontrado a correspodência para 'Quantity:' no excel informado")

    @staticmethod
    def __get_style(value: str) -> PdfParagraphStyle:
        parsed_value: int = int(value)
        font_size = 23 if parsed_value > 1 else PdfParagraphStyle.default_font_size()
        leading = PdfParagraphStyle.default_leading() + 3 if parsed_value > 1 else PdfParagraphStyle.default_leading()
        return PdfParagraphStyle(font_size=font_size, leading=leading)
