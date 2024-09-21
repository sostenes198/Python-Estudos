from library.shopee.pdf_content.pdf_content_name import ContentNameType
from library.shopee.pdf_excel_extractor import PdfExcelExtractor
from library.shopee.pdf_shopee_processor import PdfShopeeProcessor


def process(pdf_input: str, excel_input: str, pdf_output: str):
    pdf_excel_extractor = PdfExcelExtractor(ContentNameType.SKU, excel_input)
    pdf_shopee_processor = PdfShopeeProcessor(pdf_input)
    pdf_result = pdf_shopee_processor.process(pdf_excel_extractor, 20, 20, 0, 5)
    pdf_result.save_pdf(pdf_output)


def execute() -> None:
    process('../entradas/1 etiqueta - correios.pdf', '../entradas/1 etiqueta - correios.xlsx', '../saidas/1-output-correios.pdf')
    # process('../entradas/1 etiqueta.pdf', '../entradas/1 etiqueta.xlsx', '../saidas/1-output.pdf')
    # process('../entradas/2 etiqueta.pdf', '../entradas/2 etiqueta.xlsx', '../saidas/2-output.pdf')
    # process('../entradas/3 etiqueta.pdf', '../entradas/3 etiqueta.xlsx', '../saidas/3-output.pdf')
    # process('../entradas/4 etiqueta.pdf', '../entradas/4 etiqueta.xlsx', '../saidas/4-output.pdf')
    # process('../entradas/5 etiqueta.pdf', '../entradas/5 etiqueta.xlsx', '../saidas/5-output.pdf')


if __name__ == '__main__':
    execute()
