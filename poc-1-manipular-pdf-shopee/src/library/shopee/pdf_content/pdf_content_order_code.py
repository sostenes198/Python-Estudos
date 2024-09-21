from library.shopee.pdf_content.base.pdf_content import PdfContent
from library.shopee.pdf_style.pdf_paragraph_style import PdfParagraphStyle


class PdfContentOrderCode(PdfContent):
    def __init__(self, excel_content_order_sn: str):
        super().__init__(excel_content_order_sn, PdfParagraphStyle())
