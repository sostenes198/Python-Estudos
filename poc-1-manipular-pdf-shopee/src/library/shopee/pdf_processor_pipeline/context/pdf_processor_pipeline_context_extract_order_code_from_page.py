from typing import List


class ExtractOrderCodeFromPage:
    def __init__(self, order_code: str, page_number: int):
        self.__order_code: str = order_code
        self.__page_number: int = page_number

    @property
    def order_code(self) -> str:
        return self.__order_code

    @property
    def page_number(self) -> int:
        return self.__page_number


class PdfProcessorPipelineContextExtractOrderCodeFromPage:
    def __init__(self):
        self.__pages: List[ExtractOrderCodeFromPage] = []

    def add_extracted_order_code_from_page(self, order_code: str, page_number: int):
        self.__pages.append(ExtractOrderCodeFromPage(order_code, page_number))

    def get_extracted_page(self, page_number) -> ExtractOrderCodeFromPage | None:
        return next((page for page in self.__pages if page.page_number == page_number), None)
