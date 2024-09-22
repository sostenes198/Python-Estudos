from io import BytesIO

from typing import List

from library.shopee.excel_content.contents.excel_content_name import ContentNameType
from .excel_shopee_extractor import ExcelShopeeExtractor
from .pdf_processor_pipeline.base.pdf_processor_pipeline import PDFProcessorPipeline
from .pdf_processor_pipeline.base.pdf_processor_pipeline_config import PdfProcessorPipelineConfig
from .pdf_processor_pipeline.pdf_processor_pipeline_add_margin_to_pages import PdfProcessorPipelineAddMarginToPages
from .pdf_processor_pipeline.pdf_processor_pipeline_append_table_with_excel_content import \
    PdfProcessorPipelineAppendTableWithExcelContent
from .pdf_processor_pipeline.pdf_processor_pipeline_transform_quadrants_to_page import \
    PdfProcessorPipelineTransformQuadrantsToPage
from .pdf_shopee_result import PdfShopeeResult
from .shopee_config import ShopeeConfig
from ..utils.pdf.byte_io_utils import ByteIoUtils


class PdfShopeeProcessor:
    def __init__(self):
        self.__processor_pipelines: List[PDFProcessorPipeline] = [
            PdfProcessorPipelineTransformQuadrantsToPage(),
            PdfProcessorPipelineAddMarginToPages(),
            PdfProcessorPipelineAppendTableWithExcelContent()
        ]

    def process(self, config: ShopeeConfig, in_memory_pdf: str | BytesIO,
                in_memory_excel_pdf: str | BytesIO) -> PdfShopeeResult:
        __in_memory_pdf_pipeline: BytesIO = ByteIoUtils.clone(stream_or_path_file=in_memory_pdf)
        __pdf_excel_extractor: ExcelShopeeExtractor = ExcelShopeeExtractor(config.excel_config,
                                                                           in_memory_excel_pdf)
        __pdf_processor_config: PdfProcessorPipelineConfig = PdfProcessorPipelineConfig(
            original_in_memory_pdf=__in_memory_pdf_pipeline,
            pdf_extractor=__pdf_excel_extractor)

        for pipeline_processor in self.__processor_pipelines:
            __in_memory_pdf_pipeline = pipeline_processor.process(config=__pdf_processor_config,
                                                                  in_memory_pdf=__in_memory_pdf_pipeline)

        return PdfShopeeResult(ByteIoUtils.clone(__in_memory_pdf_pipeline))
