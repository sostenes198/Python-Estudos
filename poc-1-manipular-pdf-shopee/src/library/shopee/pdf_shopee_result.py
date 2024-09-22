from io import BytesIO

from pypdf import PdfReader, PdfWriter

from library.utils.pdf.byte_io_utils import ByteIoUtils


class PdfShopeeResult:
    def __init__(self, in_memory_pdf_result: BytesIO):
        self.___in_memory_pdf_result = in_memory_pdf_result

    @property
    def pdf_result_in_memory_pdf(self) -> BytesIO:
        return self.__get_in_memory_pdf_result()

    def save_pdf(self, path: str) -> None:
        reader = PdfReader(self.__get_in_memory_pdf_result())
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        # Save new PDF
        with open(path, 'wb') as output_pdf:
            writer.write(output_pdf)

    def __get_in_memory_pdf_result(self) -> BytesIO:
        return ByteIoUtils.clone(self.___in_memory_pdf_result)
