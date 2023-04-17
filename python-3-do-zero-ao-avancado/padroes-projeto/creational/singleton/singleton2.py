def singleton(the_class):
    __instances = {}

    def get_class(*args, **kwargs):
        if id(the_class) not in __instances:
            __instances[id(the_class)] = the_class(*args, **kwargs)

        return __instances[id(the_class)]

    return get_class


@singleton
class AppSettings:

    def __init__(self) -> None:
        """ O init será chamado todas as vezes """
        self.tema = 'O tema escuro'
        self.font = '18px'


if __name__ == '__main__':
    as3 = AppSettings()
    as3.tema = 'O tema claro'
    print(as3.tema)

    as4 = AppSettings()
    print(as4.tema)
