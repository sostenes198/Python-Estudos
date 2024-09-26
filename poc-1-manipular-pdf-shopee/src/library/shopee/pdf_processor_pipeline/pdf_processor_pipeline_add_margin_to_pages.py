from io import BytesIO

from pypdf import PdfReader, PdfWriter, PageObject, Transformation

from library.shopee.pdf_processor_pipeline.base.pdf_processor_pipeline import PDFProcessorPipeline
from library.shopee.pdf_processor_pipeline.context.pdf_processor_pipeline_context import PdfProcessorPipelineContext


class PdfProcessorPipelineAddMarginToPages(PDFProcessorPipeline):
    __left_margin: int = 10
    __right_margin: int = 10
    __bottom_margin: int = 0
    __top_margin: int = 10

    def __init__(self):
        super().__init__()

    def _internal_process(self, config: PdfProcessorPipelineContext, in_memory_pdf: BytesIO) -> BytesIO:
        # Open the existing PDF
        reader = PdfReader(in_memory_pdf)
        writer = PdfWriter()
        packet = BytesIO()

        # Process each page of the PDF
        for page_num in range(reader.get_num_pages()):
            page = reader.get_page(page_num)

            # Get original page dimensions
            original_width = page.mediabox.width
            original_height = page.mediabox.height

            # Calculate the available area after applying margins
            available_width = original_width - self.__left_margin - self.__right_margin
            available_height = original_height - self.__top_margin - self.__bottom_margin

            # Calculate scaling factor to fit the content within the new available space
            scale_x = available_width / original_width
            scale_y = available_height / original_height
            # scale_factor = min(scale_x, scale_y)  # Maintain aspect ratio

            # Create a new blank page with the original dimensions
            new_page = PageObject.create_blank_page(width=original_width, height=original_height)

            # Create the transformation matrix to scale and translate the original content
            transformation = (
                Transformation()
                .scale(scale_x, scale_y)  # Scale down the content to fit within margins
                .translate(self.__left_margin, self.__bottom_margin)
                # Move the content to the right and up by the margin size
            )

            # Apply the transformation to the original page and add it to the new page
            new_page.merge_transformed_page(page, transformation)
            # new_page.merge_translated_page(new_page, right_margin, top_margin)

            # Add the modified page to the writer
            writer.add_page(new_page)

        # Write the final output to the packet
        writer.write_stream(packet)
        packet.seek(0)

        return packet
