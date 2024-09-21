from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER


class PdfParagraphStyle:
    __FONT_NAME: str = 'Courier-Bold'
    __FONT_SIZE: int = 14
    __ALIGNMENT: TA_CENTER = TA_CENTER
    __LEADING: int = __FONT_SIZE * 0.9

    def __init__(self,
                 font_name=__FONT_NAME,
                 font_size=__FONT_SIZE,
                 alignment=__ALIGNMENT,
                 leading=__LEADING,):
        self.__name = 'ShopeePdfStyle'
        self.__font_name = font_name
        self.__font_size = font_size
        self.__alignment = alignment
        self.__leading = leading
        self.style: ParagraphStyle = ParagraphStyle(name=self.__name,
                                                    fontName=self.__font_name,
                                                    fontSize=self.__font_size,
                                                    alignment=self.__alignment,  # Centralized text
                                                    leading=self.__leading)  # Line spacing (can be adjusted as required

    @classmethod
    def default_font_name(cls) -> str:
        return cls.__FONT_NAME

    @classmethod
    def default_font_size(cls) -> int:
        return cls.__FONT_SIZE

    @classmethod
    def default_alignment(cls) -> TA_CENTER:
        return cls.__ALIGNMENT

    @classmethod
    def default_leading(cls) -> int:
        return cls.__LEADING
