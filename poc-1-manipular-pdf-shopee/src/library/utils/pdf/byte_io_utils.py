from io import BytesIO

from library.utils.built_in.static_class import Static


class ByteIoUtils(Static):
    @staticmethod
    def clone(stream_or_path_file: str | BytesIO) -> BytesIO:
        if isinstance(stream_or_path_file, BytesIO):
            copied_stream: BytesIO = BytesIO(stream_or_path_file.read())
            stream_or_path_file.seek(0)
            return copied_stream
        else:
            with open(stream_or_path_file, 'rb') as file:
                return BytesIO(file.read())
