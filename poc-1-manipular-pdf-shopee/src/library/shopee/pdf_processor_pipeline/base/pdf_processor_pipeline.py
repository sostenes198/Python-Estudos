from abc import ABC, abstractmethod
from io import BytesIO

from library.shopee.pdf_processor_pipeline.context.pdf_processor_pipeline_context import PdfProcessorPipelineContext
from library.utils.pdf.byte_io_utils import ByteIoUtils


class PDFProcessorPipeline(ABC):
    def __init__(self):
        ...

    def process(self, config: PdfProcessorPipelineContext, in_memory_pdf: BytesIO) -> BytesIO:
        cloned_in_memory_pdf = ByteIoUtils.clone(stream_or_path_file=in_memory_pdf)
        return self._internal_process(config=config, in_memory_pdf=cloned_in_memory_pdf)

    @abstractmethod
    def _internal_process(self, config: PdfProcessorPipelineContext, in_memory_pdf: BytesIO) -> BytesIO:
        ...
