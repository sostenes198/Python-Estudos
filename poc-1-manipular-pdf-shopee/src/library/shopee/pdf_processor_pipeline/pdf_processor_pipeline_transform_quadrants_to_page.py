from io import BytesIO
from typing import List

import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter, PageObject, Transformation
from pypdf.generic import RectangleObject

from library.shopee.pdf_processor_pipeline.base.pdf_processor_pipeline import PDFProcessorPipeline
from library.shopee.pdf_processor_pipeline.base.pdf_processor_pipeline_config import PdfProcessorPipelineConfig


class PdfProcessorPipelineTransformQuadrantsToPage(PDFProcessorPipeline):
    def __init__(self):

        super().__init__()

    def _internal_process(self, config: PdfProcessorPipelineConfig, in_memory_pdf: BytesIO) -> BytesIO:
        reader = PdfReader(in_memory_pdf)
        in_memory_pdf.seek(0)
        pdf_document: fitz.Document = fitz.open(stream=in_memory_pdf.read(), filetype="pdf")
        in_memory_pdf.seek(0)
        writer = PdfWriter()
        packet = BytesIO()

        for index in range(len(reader.pages)):
            page: PageObject = reader.pages[index]
            fitz_page: fitz.Page = pdf_document.load_page(index)
            original_right = page.mediabox.right
            original_top = page.mediabox.top

            quadrants: List[RectangleObject] = self.__list_quadrants(original_right=original_right,
                                                                     original_top=original_top)

            # For each quadrant, adjust the visible area and create a new page
            for i, quadrant in enumerate(quadrants):
                if not self.__quadrant_has_value(fitz_page=fitz_page, quadrant=quadrant,
                                                 original_top=original_top):
                    continue  # Ignore empty quadrant

                # Create blank page
                new_page = PageObject.create_blank_page(width=original_right, height=original_top)

                # Apply the quadrant cut to the original page
                page.mediabox = quadrant
                # noinspection PyTypeChecker
                page.cropbox = RectangleObject([0, 0, original_right, original_top])

                # Calculate the scale to adjust the quadrant to the size of the new page
                scale_x = original_right / quadrant.width
                scale_y = original_top / quadrant.height
                scale = min(scale_x, scale_y)

                # Apply the transformation (scaling and repositioning)
                transformation = (
                    Transformation().scale(scale).translate(-quadrant.lower_left[0] * scale,
                                                            -quadrant.lower_left[1] * scale)
                )

                # Add the quadrant content to the new page, applying the transformation
                new_page.merge_transformed_page(page, transformation)

                writer.add_page(new_page)

        writer.write_stream(packet)
        packet.seek(0)

        return packet

    @staticmethod
    def __list_quadrants(original_right: float, original_top: float) -> List[RectangleObject]:
        # Define 4 quadrants (top left, bottom left, top right, bottom right)
        # noinspection PyTypeChecker
        quadrants = [
            RectangleObject([0, original_top / 2, original_right / 2, original_top]),
            # quadrant top left
            RectangleObject([0, 0, original_right / 2, original_top / 2]),  # quadrant bottom left
            RectangleObject([original_right / 2, original_top / 2, original_right, original_top]),
            # quadrant top right
            RectangleObject([original_right / 2, 0, original_right, original_top / 2])
            # quadrant bottom right
        ]

        return quadrants

    @staticmethod
    def __quadrant_has_value(fitz_page: fitz.Page, quadrant: RectangleObject, original_top: float) -> bool:
        rect: fitz.Rect = fitz.Rect(quadrant.lower_left[0],
                                    original_top - quadrant.upper_right[1],  # Subtract to adjust the Y
                                    quadrant.upper_right[0],
                                    original_top - quadrant.lower_left[1])  # Subtract to adjust the Y

        # noinspection PyUnresolvedReferences
        text: str = fitz_page.get_text("text", clip=rect)

        return True if text else False
