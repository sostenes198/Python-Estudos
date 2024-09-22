import re
from library.shopee.excel_content.base.excel_content import ExcelContent
from library.shopee.pdf_style.pdf_paragraph_style import PdfParagraphStyle


class ExcelContentVariationName(ExcelContent):
    PATTERN_TO_FIND_VARIATION_NAME: str = r"Variation Name:(.*?);"

    def __init__(self, style: PdfParagraphStyle, excel_content_product: str):
        value = self.__extract_variation_name(excel_content_product)
        super().__init__(value, style)

    def __extract_variation_name(self, excel_content_product: str) -> str:
        match_result = re.search(self.PATTERN_TO_FIND_VARIATION_NAME, excel_content_product)
        if match_result:
            return match_result.group(1)
        else:
            raise Exception("Não encontrado a correspodência para 'Variation Name' no excel informado")
