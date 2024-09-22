from library.shopee.excel_content.contents.excel_content_name import ContentNameType


class ShopeeExcelConfig:
    def __init__(self, content_name_type: ContentNameType, font_size: int):
        self.__content_name_type: ContentNameType = content_name_type
        self.__font_size: int = font_size

    @property
    def content_name_type(self) -> ContentNameType:
        return self.__content_name_type

    @property
    def font_size(self) -> int:
        return self.__font_size


class ShopeeConfig:
    def __init__(self, shopee_excel_config: ShopeeExcelConfig):
        self.__shopee_excel_config: ShopeeExcelConfig = shopee_excel_config

    @property
    def excel_config(self) -> ShopeeExcelConfig:
        return self.__shopee_excel_config
