from io import BytesIO
from typing import Optional, List

from pypdf import PdfReader, PdfWriter, PageObject, Transformation
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table

from library.shopee.excel_content.excel_content_manager import ExcelContentManager
from library.shopee.pdf_processor_pipeline.base.pdf_processor_pipeline import PDFProcessorPipeline
from library.shopee.pdf_processor_pipeline.context.pdf_processor_pipeline_context import PdfProcessorPipelineContext
from library.shopee.pdf_processor_pipeline.context.pdf_processor_pipeline_context_extract_order_code_from_page import \
    ExtractOrderCodeFromPage
from library.shopee.pdf_style.pdf_style import PdfStyle


class PdfProcessorPipelineAppendTableWithExcelContent(PDFProcessorPipeline):
    def __init__(self):
        super().__init__()

    def _internal_process(self, config: PdfProcessorPipelineContext, in_memory_pdf: BytesIO) -> BytesIO:
        # Open pdf
        reader = PdfReader(in_memory_pdf)
        writer = PdfWriter()
        packet = BytesIO()

        # Process each page of the PDF
        for index in range(len(reader.pages)):
            page: PageObject = reader.pages[index]
            content_items: List[ExcelContentManager] = self.__list_pdf_content_items(config=config,
                                                                                     page_number=index)

            # Prepare table data
            data: List[List] = []
            for item in content_items:
                data.append([item.content_name.paragraph, item.variation_name.paragraph, item.quantity.paragraph])

            original_width = page.mediabox.width
            original_height = page.mediabox.height
            right_margin = 10
            left_margin = 10
            table_width = original_width - right_margin - left_margin

            # Create a dummy canvas to measure the table size
            dummy_canvas = canvas.Canvas(BytesIO(), pagesize=(original_width, original_height))
            table = Table(data, colWidths=[((table_width * 65) / 100), ((table_width * 20) / 100),
                                           ((table_width * 15) / 100)],
                          style=PdfStyle.table_style())
            table_width, table_height = table.wrapOn(dummy_canvas, original_width, original_height)
            translate_content_to_make_space_between_table_and_content_page = 20

            # Calculate the remaining height for the page content after the table
            remaining_height_for_content = original_height - table_height - 20

            # Create a new blank page with the original dimensions
            new_page = PageObject.create_blank_page(width=original_width, height=original_height)

            # Scale the content vertically to fit within the remaining space
            scale_factor_y = remaining_height_for_content / original_height

            # Apply vertical scaling to the content
            transformation = (
                Transformation()
                .scale(1, scale_factor_y)  # Only scale vertically
                .translate(0, table_height + translate_content_to_make_space_between_table_and_content_page)
            )

            # Merge the scaled content into the new page
            new_page.merge_transformed_page(page, transformation)

            # Build the PDF with the table
            table_packet = BytesIO()
            doc = SimpleDocTemplate(table_packet, pagesize=(original_width, original_height),
                                    rightMargin=right_margin, leftMargin=left_margin)
            doc.build([table])
            table_packet.seek(0)

            # Add the table to the new page at the bottom
            table_reader = PdfReader(table_packet)
            table_page = table_reader.pages[0]

            # Calculate the position for the table
            default_initial_position_table = 90
            new_page.merge_translated_page(table_page, 0,
                                           (original_height * -1) + table_height + default_initial_position_table)

            # Add the new page with content and table to the writer
            writer.add_page(new_page)

        # Write the final output to the packet
        writer.write_stream(packet)
        packet.seek(0)

        return packet

    @staticmethod
    def __list_pdf_content_items(config: PdfProcessorPipelineContext, page_number: int) -> List[ExcelContentManager]:
        extracted_order_code: Optional[ExtractOrderCodeFromPage] = config.context_extract_order_code_from_page.get_extracted_page(
            page_number=page_number)
        content_items: List[ExcelContentManager] = config.excel_shopee_extractor.list_pdf_contents_by_order_code(
            order_code=extracted_order_code.order_code)

        if not content_items:
            raise Exception('Nenhum pedido encontrado para o código fornecido')
        elif len(content_items) > 10:
            raise Exception('Máximo de linhas na tabela permitido por página são 10.')
        else:
            return content_items
