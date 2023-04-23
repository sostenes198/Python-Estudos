from os import listdir as os_listdir, rename as os_rename
from os.path import splitext as os_path_splitext
from typing import List


class FileNameChange(object):

    def __init__(self, directory: str) -> None:
        self.__directory = directory

    def change_file_names_from_directory(self) -> None:
        arr: List[str] = self.__list_files()
        for index, item in enumerate(arr):
            _, file_extension = os_path_splitext(item)
            path_file = f'{self.__directory}\\{item}'
            new_path_file = f'{self.__directory}\\{index + 1}{file_extension}'
            os_rename(path_file, new_path_file)

    def change_file_name_by_star_index(self, index: int) -> None:
        internal_index = index
        arr: List[str] = self.__list_files()
        for item in arr:
            _, file_extension = os_path_splitext(item)
            path_file = f'{self.__directory}\\{item}'
            new_path_file = f'{self.__directory}\\{internal_index}{file_extension}'
            os_rename(path_file, new_path_file)
            internal_index += 1

    def __list_files(self) -> List[str]:
        return os_listdir(self.__directory)


if __name__ == '__main__':
    fileNameChange = FileNameChange('C:\\Users\\soste\\Downloads\\São João Del Rei - Tiradentes 21-04-2023')
    # fileNameChange.change_file_names_from_directory()
    fileNameChange.change_file_name_by_star_index(500)
