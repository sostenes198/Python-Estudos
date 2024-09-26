from io import BytesIO
from typing import List

from pypdf import PdfReader, PageObject

from library.shopee.excel_shopee_extractor import ExcelShopeeExtractor
from library.shopee.pdf_processor_pipeline.context.pdf_processor_pipeline_context_extract_order_code_from_page import \
    PdfProcessorPipelineContextExtractOrderCodeFromPage


class PdfProcessorPipelineContext:
    def __init__(self, original_in_memory_pdf: BytesIO, excel_shopee_extractor: ExcelShopeeExtractor):
        self.__original_in_memory_pdf: BytesIO = original_in_memory_pdf
        self.__excel_shopee_extractor: ExcelShopeeExtractor = excel_shopee_extractor
        self.__context_extract_order_code_from_page = PdfProcessorPipelineContextExtractOrderCodeFromPage()

    @property
    def original_in_memory_pdf(self) -> BytesIO:
        return self.__original_in_memory_pdf

    @property
    def excel_shopee_extractor(self) -> ExcelShopeeExtractor:
        return self.__excel_shopee_extractor

    @property
    def context_extract_order_code_from_page(self) -> PdfProcessorPipelineContextExtractOrderCodeFromPage:
        return self.__context_extract_order_code_from_page
