class Static:
    def __new__(cls, *args, **kwargs):
        raise TypeError('Static classes cannot be instantiated')