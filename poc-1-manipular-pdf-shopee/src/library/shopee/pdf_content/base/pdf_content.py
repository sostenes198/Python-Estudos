from abc import ABC
from reportlab.platypus import Paragraph
from ....shopee.pdf_style.pdf_paragraph_style import PdfParagraphStyle


class PdfContent(ABC):
    def __init__(self, value: str, style: PdfParagraphStyle):
        self.__value: str = value
        self.__paragraph = Paragraph(value, style.style)

    @property
    def text_value(self) -> str:
        return self.__value

    @property
    def paragraph(self) -> Paragraph:
        return self.__paragraph
