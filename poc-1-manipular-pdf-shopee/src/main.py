from library.shopee.excel_content.contents.excel_content_name import ContentNameType
from library.shopee.pdf_shopee_processor import PdfShopeeProcessor as NewProcessor
from library.shopee.pdf_style.pdf_paragraph_style import PdfParagraphStyle
from library.shopee.shopee_config import ShopeeConfig, ShopeeExcelConfig


def process(pdf_input: str, excel_input: str, pdf_output: str):
    pdf_shopee_processor = NewProcessor()
    config: ShopeeConfig = ShopeeConfig(
        shopee_excel_config=ShopeeExcelConfig(content_name_type=ContentNameType.PRODUCT_NAME,
                                              font_size=PdfParagraphStyle.default_font_size()))
    pdf_result = pdf_shopee_processor.process(config=config, in_memory_pdf=pdf_input, in_memory_excel=excel_input)
    pdf_result.save_pdf(pdf_output)


def execute() -> None:
    process('../entradas/1 etiqueta - correios.pdf', '../entradas/1 etiqueta - correios.xlsx',
            '../saidas/1-output-correios.pdf')
    process('../entradas/1 etiqueta.pdf', '../entradas/1 etiqueta.xlsx', '../saidas/1-output.pdf')
    process('../entradas/2 etiqueta.pdf', '../entradas/2 etiqueta.xlsx', '../saidas/2-output.pdf')
    process('../entradas/3 etiqueta.pdf', '../entradas/3 etiqueta.xlsx', '../saidas/3-output.pdf')
    process('../entradas/4 etiqueta.pdf', '../entradas/4 etiqueta.xlsx', '../saidas/4-output.pdf')
    process('../entradas/5 etiqueta.pdf', '../entradas/5 etiqueta.xlsx', '../saidas/5-output.pdf')
    process('../entradas/6 etiqueta.pdf', '../entradas/6 etiqueta.xlsx', '../saidas/6-output.pdf')


if __name__ == '__main__':
    execute()
