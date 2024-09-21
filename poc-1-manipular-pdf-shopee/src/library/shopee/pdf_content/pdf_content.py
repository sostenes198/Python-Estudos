from .pdf_content_order_code import PdfContentOrderCode
from .pdf_content_name import PdfContentName
from .pdf_content_variation_name import PdfContentVariationName
from .pdf_content_quantity import PdfContentQuantity


class PdfContent:
    def __init__(self, content_order_code: PdfContentOrderCode, content_name: PdfContentName,
                 variation_name: PdfContentVariationName,
                 quantity: PdfContentQuantity):
        self.__content_order_code: PdfContentOrderCode = content_order_code
        self.__content_name: PdfContentName = content_name
        self.__variation_name: PdfContentVariationName = variation_name
        self.__quantity: PdfContentQuantity = quantity

    @property
    def content_order_code(self) -> PdfContentOrderCode:
        return self.__content_order_code

    @property
    def content_name(self) -> PdfContentName:
        return self.__content_name

    @property
    def variation_name(self) -> PdfContentVariationName:
        return self.__variation_name

    @property
    def quantity(self) -> PdfContentQuantity:
        return self.__quantity
