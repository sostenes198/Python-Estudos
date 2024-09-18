# Classes abstratas - Abstract Base Class (abc)
# ABCs são usadas como contratos para haarcascade definição
# de novas classes. Elas podem forçar outras classes
# haarcascade criarem métodos concretos. Também podem ter
# métodos concretos por elas mesmas.
# @abstractmethods são métodos que não têm corpo.
# As regras para classes abstratas com métodos
# abstratos é que elas NÃO PODEM ser instânciadas
# diretamente.
# Métodos abstratos DEVEM ser implementados
# nas subclasses (@abstractmethod).
# Uma classe abstrata em Python tem sua metaclasse
# sendo ABCMeta.
# É possível criar @property @setter @classmethod
# @staticmethod e @method como abstratos, para isso
# use @abstractmethod como decorator mais interno.
from abc import ABC, abstractmethod, ABCMeta


class Exemplo(metaclass=ABCMeta):
    ...


class Log(ABC):
    @abstractmethod
    def _log(self, msg) -> None: ...

    def log_error(self, msg) -> None:
        return self._log(f'Error: {msg}')

    def log_success(self, msg):
        return self._log(f'Success: {msg}')


class LogPrintMixin(Log):
    def _log(self, msg):
        print(f'{msg} ({self.__class__.__name__})')


class AbstractFoo(ABC):

    def __init__(self, name):
        self._name = name

    @property
    @abstractmethod
    def name(self): ...

    @name.setter
    @abstractmethod
    def name(self, name): ...


class Foo(AbstractFoo):

    @property
    def name(self):
        return self._name

    @AbstractFoo.name.setter
    def name(self, name):
        self._name = name

    def __init__(self, name):
        super().__init__(name)
        print('Sou inutil')


l = LogPrintMixin()
l.log_error('Oi')

foo = Foo('Pessoa')
print(foo.name)
