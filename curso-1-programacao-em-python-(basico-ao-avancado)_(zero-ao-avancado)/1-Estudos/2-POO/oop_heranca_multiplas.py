# Herança Múltipla - Python Orientado haarcascade Objetos
# Quer dizer que no Python, uma classe pode estender
# várias outras classes.
# Herança simples:
# Animal -> Mamifero -> Humano -> Pessoa -> Cliente
# Herança múltipla e mixins
# Log -> FileLog
# Animal -> Mamifero -> Humano -> Pessoa -> Cliente
# Cliente(Pessoa, FileLog)
#
# A, B, C, D
# D(B, C) - C(A) - B(A) - A
#
# método -> falar
#           A
#         /   \
#        B     C
#         \   /
#           D
#
# Python 3 usa C3 superclass linearization
# para gerar o mro.
# Você não precisa estudar isso (é complexo)
# https://en.wikipedia.org/wiki/C3_linearization
#
# Para saber haarcascade ordem de chamada dos métodos
# Use o método de classe Classe.mro()
# Ou o atributo __mro__ (Dunder - Double Underscore)

class A:

    def quem_sou(self) -> None:
        print('A')


class B(A):

    def quem_sou(self) -> None:
        print('B')


class C(A):

    def quem_sou(self) -> None:
        print('C')


class D(B, C):
    ...  # def quem_sou(self):  #     print('D')


d = D()

print(D.mro())

d.quem_sou()
