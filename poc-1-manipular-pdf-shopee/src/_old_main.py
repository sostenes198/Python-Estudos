from typing import List, Optional
from pypdf import PdfReader, PdfWriter, Transformation, PageObject
from pypdf.generic import RectangleObject
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.pdfgen import canvas
from io import BytesIO
import fitz  # PyMuPDF
import pdfplumber
import pandas as pd
import re


class ContentExtractedExcel:
    def __init__(self, order_code: str,
                 variation_name: str,
                 sku_reference: str,
                 quantity: str,
                 max_lines: int):
        self.orderCode = order_code
        self.variationName = variation_name
        self.skuReference = sku_reference
        self.quantity = quantity
        self.maxLines = max_lines


def split_pdf_into_quadrants(input_pdf: BytesIO) -> BytesIO:
    reader = PdfReader(input_pdf)
    input_pdf.seek(0)
    pdf_document = fitz.open(stream=input_pdf.read(), filetype="pdf")
    input_pdf.seek(0)
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
            RectangleObject([original_width / 2, 0, original_width, original_height / 2])  # quadrant bottom right
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


def add_margin_to_page(input_pdf_stream: BytesIO, left_margin: int, right_margin: int, bottom_margin: int,
                       top_margin: int) -> BytesIO:
    # Open the existing PDF
    reader = PdfReader(input_pdf_stream)
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


def get_content_from_excel(excel_context: pd.DataFrame) -> List[ContentExtractedExcel]:
    pattern_to_split_product_info_in_array = r'(?=\[\d+\])'
    pattern_to_find_variation_name = r"Variation Name:(.*?);"
    pattern_to_find_quantity = r"Quantity:(.*?);"
    pattern_to_find_sku_reference = r"SKU Reference No\.:(.*?);"
    format_count_splot = 44

    result: List[ContentExtractedExcel] = []

    for _, row in excel_context.iterrows():
        order_sn: str = row['order_sn']
        product_infos: str = row['product_info']

        products = [part.strip() for part in re.split(pattern_to_split_product_info_in_array, product_infos) if
                    part.strip()]

        for product_info in products:
            match_variation_name = re.search(pattern_to_find_variation_name, product_info)
            match_quantity = re.search(pattern_to_find_quantity, product_info)
            match_sku_reference = re.search(pattern_to_find_sku_reference, product_info)

            if match_variation_name and match_quantity and match_sku_reference:
                result.append(ContentExtractedExcel(order_code=order_sn,
                                                    variation_name=match_variation_name.group(1),
                                                    quantity=match_quantity.group(1),
                                                    sku_reference=match_sku_reference.group(1),
                                                    max_lines=len(products))
                              )
            else:
                raise Exception('Não encontrado as correspondências necessárias')

    return result


def add_content(input_pdf_stream: BytesIO, content_extracted_excel: List[ContentExtractedExcel]) -> BytesIO:
    # Open pdf
    reader = PdfReader(input_pdf_stream)
    writer = PdfWriter()
    packet = BytesIO()

    # Customized style for paragraphs, including font size, alignment and font
    custom_style = ParagraphStyle(
        name="CustomStyle",
        fontName="Courier-Bold",  # Definir a fonte como Courier-Bold
        fontSize=20,  # Definir o tamanho da fonte
        alignment=TA_CENTER,  # Centralizar o texto
        leading=20,  # Espaçamento entre linhas (pode ajustar conforme necessário)
    )

    # Process each page of the PDF
    for index in range(len(reader.pages)):
        page = reader.pages[index]

        with pdfplumber.open(input_pdf_stream) as pdf:
            first_page = pdf.pages[index]
            words = first_page.within_bbox(page.mediabox).extract_words()
            first_occurrence: str = next((word for word in words if word['text'].startswith("Pedido:")), None)['text']
            order_code = first_occurrence.split(":")[1]

        content_items: List[Optional[ContentExtractedExcel]] = [item for item in content_extracted_excel if
                                                                item.orderCode == order_code]

        if content_items is None:
            raise Exception('Nenhum pedido encontrado para o código fornecido')

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

        # Table data (one row and three columns)
        # max_characters = 484 to column in table
        data: List[List] = []
        for item in content_items:
            data.append([
                Paragraph(item.skuReference, custom_style),
                Paragraph(item.variationName, custom_style),
                Paragraph(item.quantity, custom_style)
            ])

        # Create table
        table = Table(data,
                      colWidths=[table_width * 0.5, table_width * 0.4, table_width * 0.1],
                      style=TableStyle([
                          ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Borders throughout the table
                          # ('BACKGROUND', (0, 0), (-1, 0), colors.white),  # Header line background
                          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center the text
                          ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Align vertically in the middle
                          ('FONTSIZE', (0, 0), (-1, -1), 20),  # Setting the font size
                          ('FONTNAME', (0, 0), (-1, -1), 'Courier-Bold'),  # Define font type
                      ]))

        # Width and Height of table
        width_table, height_table = table.wrapOn(dummy_canvas, width, height)

        initial_height_to_translate = 90
        max_lines = max(content_items, key=lambda item: item.maxLines).maxLines
        if max_lines > 10:
            raise Exception('Máximo de linhas na tabela permitido por página são 10.')
        else:
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


def save_pdf(input_pdf: BytesIO, output_path):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    # Save new PDF
    with open(output_path, 'wb') as output_pdf:
        writer.write(output_pdf)


def process(pdf_input: str, excel_input: str, pdf_output: str):
    with open(pdf_input, 'rb') as file:
        packet = split_pdf_into_quadrants(BytesIO(file.read()), )
        # packet = add_margin_to_page(packet, 5, 5, 0, 5)

        content_extracted_excel = get_content_from_excel(pd.read_excel(excel_input))
        packet = add_content(packet, content_extracted_excel)
        save_pdf(packet, pdf_output)


def execute() -> None:
    process('../entradas/1 etiqueta.pdf', '../entradas/1 etiqueta.xlsx', '../saidas/1-output.pdf')
    # process('../entradas/2 etiqueta.pdf', '../entradas/2 etiqueta.xlsx', '../saidas/2-output.pdf')
    # process('../entradas/3 etiqueta.pdf', '../entradas/3 etiqueta.xlsx', '../saidas/3-output.pdf')
    # process('../entradas/4 etiqueta.pdf', '../entradas/4 etiqueta.xlsx', '../saidas/4-output.pdf')
    # process('../entradas/5 etiqueta.pdf', '../entradas/5 etiqueta.xlsx', '../saidas/5-output.pdf')


if __name__ == '__main__':
    execute()
