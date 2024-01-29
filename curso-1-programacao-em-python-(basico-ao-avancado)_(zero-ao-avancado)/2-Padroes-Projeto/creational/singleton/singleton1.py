"""
O Singleton tem a intenção de garantir que uma classe tenha somente
uma instância e fornece um ponto global de acesso para a mesma.
When discussing which patterns to drop, we found
that we still love them all.
(Not really—I'm in favor of dropping Singleton.
Its use is almost always a design smell.)
- Erich Gamma, em entrevista para informIT
http://www.informit.com/articles/article.aspx?p=1404056
"""


class AppSettings:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self) -> None:
        """ O init será chamado todas as vezes """
        self.tema = 'O tema escuro'
        self.font = '18px'


if __name__ == '__main__':
    as1 = AppSettings()
    as2 = AppSettings()

    print(as1)
    print(as2)
    print(id(as1))
    print(id(as2))
    print(id(as1) == id(as2))

    as3 = AppSettings()
    as3.tema = 'O tema claro'
    print(as3.tema)
    
    as4 = AppSettings()
    print(as4.tema)
