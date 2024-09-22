from io import BytesIO
from typing import List

from pypdf import PdfReader, PageObject

from library.shopee.excel_shopee_extractor import ExcelShopeeExtractor


class PdfProcessorPipelineConfigPage:
    def __init__(self, original_width: float, original_height: float):
        self.__original_width = original_width
        self.__original_height = original_height


class PdfProcessorPipelineConfig:
    def __init__(self, original_in_memory_pdf: BytesIO, pdf_extractor: ExcelShopeeExtractor):
        self.__pages_config: List[PdfProcessorPipelineConfigPage] = []
        self.__pdf_extractor: ExcelShopeeExtractor = pdf_extractor

        self.__read_pages(original_in_memory_pdf)

    @property
    def pdf_extractor(self) -> ExcelShopeeExtractor:
        return self.__pdf_extractor

    def __read_pages(self, original_in_memory_pdf: BytesIO) -> None:
        reader = PdfReader(original_in_memory_pdf)

        for index in range(len(reader.pages)):
            page: PageObject = reader.pages[index]
            self.__pages_config.append(
                PdfProcessorPipelineConfigPage(original_width=page.mediabox.width, original_height=page.mediabox.height))

        original_in_memory_pdf.seek(0)
