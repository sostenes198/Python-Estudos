# dataclasses - O que são dataclasses?
# O módulo dataclasses fornece um decorador e funções para criar métodos como
# __init__(), __repr__(), __eq__() (entre outros) em classes definidas pelo
# usuário.
# Em resumo: dataclasses são syntax sugar para criar classes normais.
# Foi descrito na PEP 557 e adicionado na versão 3.7 do Python.
# doc: https://docs.python.org/3/library/dataclasses.html
from dataclasses import dataclass, asdict, astuple, field


@dataclass(init=False)
class Pessoa:
    nome: str = field(default='Missing', repr=False)
    sobrenome: int = field(default=0)
    enderecos: list[str] = field(default_factory=list)

    def __post_init__(self):
        print('Post Init')
        self.nome_completo = f'{self.nome} {self.sobrenome}'

    # @property  # def nome_completo(self):  #     return f'{self.nome} {self.idade}'  #   # @nome_completo.setter  # def nome_completo(self, nome, sobrenome):  #     self.nome = nome  #     self.sobrenome = sobrenome


if __name__ == '__main__':
    p1 = Pessoa('Luiz', 30)
    p2 = Pessoa('Luiz', 30)
    print(p1 == p2)
    print(asdict(p1))
    print(astuple(p2))
