import re
from io import BytesIO

from typing import Optional, Any, List

from pypdf import PdfReader, PdfWriter, Transformation, PageObject
from pypdf.generic import RectangleObject
import fitz  # PyMuPDF
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table

from .pdf_content.pdf_content import PdfContent
from .pdf_excel_extractor import PdfExcelExtractor
from .pdf_shopee_result import PdfShopeeResult
from .pdf_style.pdf_style import PdfStyle


class PdfShopeeProcessor:
    def __init__(self, path: str):
        self.__original_pdf_in_memory = self.__read_file(path)
        self.__in_memory_pdf_pipeline = BytesIO(self.__original_pdf_in_memory.read())
        self.__in_memory_pdf_pipeline.seek(0)
        self.__original_pdf_in_memory.seek(0)

    def process(self, pdf_excel_extractor: PdfExcelExtractor, left_margin: int, right_margin: int, bottom_margin: int,
                top_margin: int) -> PdfShopeeResult:
        self.__in_memory_pdf_pipeline = self.__split_pdf_into_quadrants(self.__in_memory_pdf_pipeline)
        self.__in_memory_pdf_pipeline = self.__add_margin_to_page(self.__in_memory_pdf_pipeline,
                                                                  left_margin,
                                                                  right_margin,
                                                                  bottom_margin,
                                                                  top_margin)
        self.__in_memory_pdf_pipeline = self.__add_content(pdf_excel_extractor, self.__in_memory_pdf_pipeline)
        self.__in_memory_pdf_pipeline.seek(0)

        return PdfShopeeResult(self.__in_memory_pdf_pipeline)

    def __split_pdf_into_quadrants(self, in_memory_pdf: BytesIO) -> BytesIO:
        reader = PdfReader(in_memory_pdf)
        in_memory_pdf.seek(0)
        pdf_document = fitz.open(stream=in_memory_pdf.read(), filetype="pdf")
        in_memory_pdf.seek(0)
        writer = PdfWriter()
        packet = BytesIO()

        for index in range(len(reader.pages)):
            page: PageObject = reader.pages[index]
            fitz_page: fitz.Page = pdf_document.load_page(index)

            original_width = page.mediabox.right
            original_height = page.mediabox.top

            # Define 4 quadrants (top left, bottom left, top right, bottom right)
            # noinspection PyTypeChecker
            quadrants = [
                RectangleObject([0, original_height / 2, original_width / 2, original_height]),
                # quadrant top left
                RectangleObject([0, 0, original_width / 2, original_height / 2]),  # quadrant bottom left
                RectangleObject([original_width / 2, original_height / 2, original_width, original_height]),
                # quadrant top right
                RectangleObject([original_width / 2, 0, original_width, original_height / 2])
                # quadrant bottom right
            ]

            # For each quadrant, adjust the visible area and create a new page
            for i, quadrant in enumerate(quadrants):
                rect: fitz.Rect = fitz.Rect(quadrant.lower_left[0],
                                            original_height - quadrant.upper_right[1],  # Subtract to adjust the Y
                                            quadrant.upper_right[0],
                                            original_height - quadrant.lower_left[1])  # Subtract to adjust the Y

                # noinspection PyUnresolvedReferences
                text: str = fitz_page.get_text("text", clip=rect)

                if not text:
                    continue  # Ignore empty quadrant

                # Create blank page
                new_page = PageObject.create_blank_page(width=original_width, height=original_height)

                # Apply the quadrant cut to the original page
                page.mediabox = quadrant
                # noinspection PyTypeChecker
                page.cropbox = RectangleObject([0, 0, original_width, original_height])

                # Calculate the scale to adjust the quadrant to the size of the new page
                scale_x = original_width / quadrant.width
                scale_y = original_height / quadrant.height
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

    def __add_margin_to_page(self, in_memory_pdf: BytesIO, left_margin: int, right_margin: int, bottom_margin: int,
                             top_margin: int) -> BytesIO:
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

            # Calculate new dimensions with margin
            new_width = original_width + left_margin + right_margin
            new_height = original_height + bottom_margin + top_margin

            # Create a new page with the adjusted dimensions
            new_page = page.create_blank_page(width=new_width, height=new_height)

            # Add the original page to the center of the new page
            new_page.merge_translated_page(page, left_margin, bottom_margin)

            writer.add_page(new_page)

        writer.write_stream(packet)
        packet.seek(0)

        return packet

    def __add_content(self, pdf_excel_extractor: PdfExcelExtractor, in_memory_pdf: BytesIO) -> BytesIO:
        # Open pdf
        reader = PdfReader(in_memory_pdf)
        writer = PdfWriter()
        packet = BytesIO()

        # Process each page of the PDF
        for index in range(len(reader.pages)):
            page: PageObject = reader.pages[index]
            order_code: Optional[str] = self.__extract_order_code_from_page(page, index, in_memory_pdf)
            content_items: List[PdfContent] = self.__list_pdf_content_items(pdf_excel_extractor, order_code)
            data: List[List] = []
            for item in content_items:
                data.append([item.content_name.paragraph, item.variation_name.paragraph, item.quantity.paragraph])

            table_packet = BytesIO()
            width = page.mediabox.width
            height = page.mediabox.height
            right_margin = 10
            left_margin = 10
            table_width = width - right_margin - left_margin

            # Create a canvas to use with wrapOn()
            dummy_canvas = canvas.Canvas(BytesIO(), pagesize=(width, height))

            # Create a new page with the table
            doc = SimpleDocTemplate(table_packet, pagesize=(width, height), rightMargin=right_margin,
                                    leftMargin=left_margin)

            # Create table
            table = Table(data,
                          colWidths=[table_width * 0.5, table_width * 0.4, table_width * 0.1],
                          style=PdfStyle.table_style())

            # Width and Height of table
            width_table, height_table = table.wrapOn(dummy_canvas, width, height)

            # height to translate
            initial_height_to_translate = 90
            height_to_translate = initial_height_to_translate + height_table

            # Build the PDF with the table
            doc.build([table])
            table_packet.seek(0)

            table_reader = PdfReader(table_packet)
            table_page = table_reader.pages[0]

            # Create a new page for the final PDF
            new_page = page.create_blank_page(width=width, height=height + height_table + 20)

            # Add the original page and table to the new page
            new_page.merge_translated_page(page, 0, height_table + 20)

            new_page.merge_translated_page(table_page, 0, (height * -1) + height_to_translate)

            writer.add_page(new_page)

            writer.write_stream(packet)
            packet.seek(0)

        return packet

    @staticmethod
    def __extract_order_code_from_page(page: PageObject, index_page: int, in_memory_pdf: BytesIO) \
            -> Optional[str]:

        order_code_shopee: Optional[str] = PdfShopeeProcessor.__extract_order_code_from_page_shopee(page, index_page,
                                                                                                    in_memory_pdf)

        order_code_correios: Optional[str] = PdfShopeeProcessor.__extract_order_code_from_page_correios(page,
                                                                                                        index_page,
                                                                                                        in_memory_pdf)

        if not order_code_shopee and not order_code_correios:
            raise Exception('Não encontrado número do pedido na página do PDF.')

        return order_code_shopee or order_code_correios

    @staticmethod
    def __extract_order_code_from_page_shopee(page: PageObject, index_page: int, in_memory_pdf: BytesIO) \
            -> Optional[str]:
        with pdfplumber.open(in_memory_pdf) as pdf:
            first_page = pdf.pages[index_page]
            words = first_page.within_bbox(page.mediabox).extract_words()
            first_occurrence: Optional[dict[str, Any]] = next(
                (word for word in words if word['text'].startswith("Pedido:")), None)
            if first_occurrence is None:
                return None

            order_code: Optional[str] = first_occurrence['text'].split(":")[1]

        return order_code

    @staticmethod
    def __extract_order_code_from_page_correios(page: PageObject, index_page: int, in_memory_pdf: BytesIO) \
            -> Optional[str]:
        with pdfplumber.open(in_memory_pdf) as pdf:
            first_page = pdf.pages[index_page]
            words = first_page.within_bbox(page.mediabox).extract_text()
            math_result = re.search(r'ID pedido:[A-Za-z0-9\s]+[\D]+\s*([A-Za-z0-9\s]+)\s', words)
            if math_result:
                return math_result.group(1)
            return None

    @staticmethod
    def __list_pdf_content_items(pdf_excel_extractor: PdfExcelExtractor,
                                 order_code: Optional[str]) -> List[PdfContent]:
        content_items: List[PdfContent] = pdf_excel_extractor.list_pdf_contents_by_order_code(order_code)
        if not content_items:
            raise Exception('Nenhum pedido encontrado para o código fornecido')
        elif len(content_items) > 10:
            raise Exception('Máximo de linhas na tabela permitido por página são 10.')
        else:
            return content_items

    @staticmethod
    def __read_file(path: str) -> BytesIO:
        with open(path, 'rb') as file:
            return BytesIO(file.read())
