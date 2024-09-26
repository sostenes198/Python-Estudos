from io import BytesIO
from typing import List

import pdfplumber
from pypdf import PdfReader, PageObject

from library.shopee.excel_content.contents.excel_content_order_code import ExcelContentOrderCode
from library.shopee.pdf_processor_pipeline.base.pdf_processor_pipeline import PDFProcessorPipeline
from library.shopee.pdf_processor_pipeline.context.pdf_processor_pipeline_context import PdfProcessorPipelineContext


class PdfProcessorPipelineExtractOrderCodeFromPage(PDFProcessorPipeline):
    def __init__(self):
        super().__init__()

    def _internal_process(self, config: PdfProcessorPipelineContext, in_memory_pdf: BytesIO) -> BytesIO:
        # Open pdf
        reader = PdfReader(in_memory_pdf)
        content_order_codes: List[
            ExcelContentOrderCode] = config.excel_shopee_extractor.list_order_codes_from_excel_contents()

        for index in range(len(reader.pages)):
            page: PageObject = reader.pages[index]
            order_code: str | None = None

            with pdfplumber.open(in_memory_pdf) as pdf:
                first_page = pdf.pages[index]
                text = first_page.within_bbox(page.mediabox).extract_text()
                for content_order_code in content_order_codes:
                    if content_order_code.text_value in text:
                        order_code = content_order_code.text_value
                        break

            if not order_code:
                raise Exception('Não encontrado número do pedido na página do PDF.')

            config.context_extract_order_code_from_page.add_extracted_order_code_from_page(order_code=order_code,
                                                                                           page_number=index)

        in_memory_pdf.seek(0)
        return in_memory_pdf
