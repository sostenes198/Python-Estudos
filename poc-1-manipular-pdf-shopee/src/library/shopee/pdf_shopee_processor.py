from io import BytesIO

from typing import List

from .excel_shopee_extractor import ExcelShopeeExtractor
from .pdf_processor_pipeline.base.pdf_processor_pipeline import PDFProcessorPipeline
from library.shopee.pdf_processor_pipeline.context.pdf_processor_pipeline_context import PdfProcessorPipelineContext
from .pdf_processor_pipeline.pdf_processor_pipeline_add_audit_text_on_top_page import \
    PdfProcessorPipelineAddAuditTextOnTopPage
from .pdf_processor_pipeline.pdf_processor_pipeline_add_margin_to_pages import PdfProcessorPipelineAddMarginToPages
from .pdf_processor_pipeline.pdf_processor_pipeline_append_table_with_excel_content import \
    PdfProcessorPipelineAppendTableWithExcelContent
from .pdf_processor_pipeline.pdf_processor_pipeline_extract_order_code_from_page import \
    PdfProcessorPipelineExtractOrderCodeFromPage
from .pdf_processor_pipeline.pdf_processor_pipeline_transform_quadrants_to_page import \
    PdfProcessorPipelineTransformQuadrantsToPage
from .pdf_shopee_result import PdfShopeeResult
from .shopee_config import ShopeeConfig
from ..utils.pdf.byte_io_utils import ByteIoUtils


class PdfShopeeProcessor:
    def __init__(self):
        self.__processor_pipelines: List[PDFProcessorPipeline] = [
            PdfProcessorPipelineTransformQuadrantsToPage(),
            PdfProcessorPipelineAddAuditTextOnTopPage(),
            PdfProcessorPipelineExtractOrderCodeFromPage(),
            PdfProcessorPipelineAddMarginToPages(),
            PdfProcessorPipelineAppendTableWithExcelContent()
        ]

    def process(self, config: ShopeeConfig, in_memory_pdf: str | BytesIO,
                in_memory_excel: str | BytesIO) -> PdfShopeeResult:
        __in_memory_pdf_pipeline: BytesIO = ByteIoUtils.clone(stream_or_path_file=in_memory_pdf)
        __pdf_excel_extractor: ExcelShopeeExtractor = ExcelShopeeExtractor(config=config.excel_config,
                                                                           excel_file_path_or_stream=in_memory_excel)
        __pdf_processor_config: PdfProcessorPipelineContext = PdfProcessorPipelineContext(
            original_in_memory_pdf=__in_memory_pdf_pipeline,
            excel_shopee_extractor=__pdf_excel_extractor)

        for pipeline_processor in self.__processor_pipelines:
            __in_memory_pdf_pipeline = pipeline_processor.process(config=__pdf_processor_config,
                                                                  in_memory_pdf=__in_memory_pdf_pipeline)

        return PdfShopeeResult(__in_memory_pdf_pipeline)
