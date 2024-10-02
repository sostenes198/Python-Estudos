from io import BytesIO
from datetime import datetime

from pypdf import PdfReader, PdfWriter, PageObject, Transformation

from reportlab.pdfgen import canvas

from library.shopee.pdf_processor_pipeline.base.pdf_processor_pipeline import PDFProcessorPipeline
from library.shopee.pdf_processor_pipeline.context.pdf_processor_pipeline_context import PdfProcessorPipelineContext
from library.shopee.pdf_style.pdf_paragraph_style import PdfParagraphStyle


class PdfProcessorPipelineAddAuditTextOnTopPage(PDFProcessorPipeline):
    def __init__(self):
        super().__init__()


    def _internal_process(self, config: PdfProcessorPipelineContext, in_memory_pdf: BytesIO) -> BytesIO:
        # Open the existing PDF
        reader = PdfReader(in_memory_pdf)
        writer = PdfWriter()
        packet = BytesIO()

        date_text = datetime.now().strftime("%d/%m/%y %H:%M:%S")
        total_pages = reader.get_num_pages()

        # Define how much to move the content down to create space for the header
        header_height = 12  # Height for the header space

        # Process each page of the PDF
        for page_num in range(total_pages):
            page = reader.get_page(page_num)

            # Get original page dimensions
            original_width = page.mediabox.width
            original_height = page.mediabox.height

            # Move the content of the original page down by applying a translation
            transformation = Transformation().translate(0, -header_height)  # Move content down
            page.add_transformation(transformation)

            # Height margin
            height_margin = 10

            # Now let's create a temporary PDF in memory for the header (date and page number)
            header_packet = BytesIO()
            can = canvas.Canvas(header_packet, pagesize=(original_width, original_height))

            # Set font and size for the date and page number
            can.setFont(PdfParagraphStyle.default_font_name(), PdfParagraphStyle.default_font_size())

            # Add date on the top left (adjust Y to account for ReportLab's coordinate system)
            can.drawString(0, original_height - height_margin, date_text)

            # Add page number on the top right
            page_text = f"{page_num + 1}/{total_pages}"
            can.drawRightString(original_width, original_height - height_margin, page_text)

            can.save()

            # Move to the beginning of the StringIO buffer
            header_packet.seek(0)

            # Merge the header (date and page number) onto the original page
            header_pdf = PdfReader(header_packet)
            header_page = header_pdf.get_page(0)

            # Merge the header on the original page content
            page.merge_page(header_page)

            # Add the modified page to the writer
            writer.add_page(page)

        # Write the final output to the packet
        writer.write(packet)
        packet.seek(0)

        return packet