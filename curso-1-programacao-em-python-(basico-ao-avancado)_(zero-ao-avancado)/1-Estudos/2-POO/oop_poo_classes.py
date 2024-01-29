"""Documentação do modulo"""

import json
from abc import ABC, abstractmethod
from decorator_decorators import LogDecorator, MyReprDecorator
from typing import List, Dict, Generator, Self, Any
from inspect import signature
from Estudos.POO.log import LogPrintMixin


class Animal(ABC):

    def __init__(self, nome: str):
        self._nome = nome

    @property
    def nome(self) -> str:
        return self._nome

    @nome.setter
    @abstractmethod
    def nome(self, nome: str) -> None: ...


class Pessoa(Animal, LogPrintMixin):
    cpf = 'CPF PESSOA'
    caminho_arquivo = "aula198_pessoa.json"

    @Animal.nome.setter
    def nome(self, nome: str) -> None:
        self._nome = nome

    @property
    def sobrenome(self) -> str:
        return self.__sobrenome
    
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, nome: str, sobrenome: str) -> None:
        super().__init__(nome)
        self.__sobrenome = sobrenome

    def __str__(self) -> str:
        return f'{self.nome} {self.sobrenome}'

    def __repr__(self) -> str:
        class_name = type(self).__name__
        return f'{class_name}(nome={self.nome!r} sobrenome={self.sobrenome!r})'

    @classmethod
    @LogDecorator
    def criar_familia(cls, nomes: List[str], sobrenome: str) -> List[Self]:
        return [cls(nome, sobrenome) for nome in nomes]

    def comer(self) -> str:
        super().log_success("Comeu fofo")
        return f'{self.nome} {self.sobrenome} está comendo.'

    def falar_nome_classe(self) -> None:
        print(self.nome, self.sobrenome, self.__class__.__name__)

    def mostrar_mro(self) -> None:
        """Mro Method Resolution Order"""
        print(self.__class__.__mro__)  # help(self)  # self.__class__.mro()

    @classmethod
    def serializar_pessoas_em_json(cls, pessoas: List[Self]) -> None:
        pessoas_convertidas: Dict[str, Any] = [vars(pessoa) for pessoa in pessoas]
        with open(cls.caminho_arquivo, 'w') as arquivo:
            json.dump(pessoas_convertidas, arquivo, ensure_ascii=False, indent=2)

    @classmethod
    def desserializar_pessoas_de_json(cls) -> List[Self]:
        with open(cls.caminho_arquivo, 'r') as arquivo:
            pessoas_json: List[Dict[str, Any]] = json.load(arquivo)
            init_parametros: List[str] = list(signature(cls.__init__).parameters.keys())[1::]
            fix_json_parametros: Generator[zip[tuple[str, Any]], Any, None] = (zip(init_parametros, dic.values()) for dic in pessoas_json)
            return [Pessoa(**dict[str, Any](parametros)) for parametros in fix_json_parametros]

    @staticmethod
    def static_metodo(*args: tuple[Any], **kwargs: dict[str, Any]) -> None:
        print(args)
        print(kwargs)

    def falar(self):
        print(f'Falando {self.__class__.__name__}')


@MyReprDecorator('Mensagem Inicial')
class Aluno(Pessoa):

    cpf = 'CPF ALUNO'

    def falar(self):
        print(f'Falando {self.__class__.__name__}')


class Professor(Pessoa):

    cpf = 'CPF PROFESSOR'

    def falar(self):
        print(f'Falando {self.__class__.__name__}')


class Executor():
    
    def __call__(self, pessoa: Pessoa) -> None:
        print('Executando "Executador" pelo método __call__')
        pessoa.falar()
        
    def fala(self, pessoa: Pessoa):
        pessoa.falar()


p1 = Pessoa("Soso", "Souza")
p2 = Pessoa("Raquel", "Gontijo")
p3 = Pessoa('MeninoEd', 'Alves')

p1.test_atribute = "Valor1"

print(p1.__dict__)

del p1.test_atribute

print(p1.__dict__)

print(type(p1.__dict__))

print(p1.comer())

print(Pessoa.comer(p1))

Pessoa.serializar_pessoas_em_json([p1, p2, p3])

pessoas: List[Pessoa] = Pessoa.desserializar_pessoas_de_json()

print(pessoas)
print(type(pessoas[0]))

familia: list[Pessoa] = Pessoa.criar_familia(["Soso", "Raquel", "Majunio", "Mamis", "Papis"], "Souza")

print(familia)

Pessoa.static_metodo("123", 321, Value1="123321", Value2="321312")

aluno = Aluno("Soso", "Souza")
professor = Professor("Raquel", "Fonseca")

print(repr(aluno))

aluno.falar_nome_classe()
professor.falar_nome_classe()

print(p1.cpf)
print(aluno.cpf)
print(professor.cpf)

p1.mostrar_mro()
aluno.mostrar_mro()
professor.mostrar_mro()

executor = Executor()
executor.fala(p1)
executor.fala(aluno)
executor.fala(professor)

executor(p1)
executor(aluno)
executor(professor)

print(p1)
print(repr(p2))
print(f'{p2!s}')
print(f'{p2!r}')