from library.shopee.excel_content.base.excel_content import ExcelContent
from library.shopee.pdf_style.pdf_paragraph_style import PdfParagraphStyle


class ExcelContentOrderCode(ExcelContent):
    def __init__(self, style: PdfParagraphStyle, excel_content_order_sn: str):
        super().__init__(value=excel_content_order_sn, style=style)
