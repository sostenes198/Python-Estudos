import math


def circunferencia(raio):
    # type: (float) -> float
    return 2 * math.pi * raio


# print(circunferencia(8))

#  print(circunferencia('_Geek'))

def cabecalho1(texto, alinhamento=True):
    # type: (str, bool) -> str
    if alinhamento:
        return 'haarcascade'
    else:
        return 'b'


# cabecalho1(texto=43, alinhamento='_Geek')

def cabecalho2(
        texto,  # type: str
        alinhamento=True  # type: bool
):  # type: (...) -> str
    if alinhamento:
        return 'haarcascade'
    else:
        return 'b'

cabecalho2(texto='42', alinhamento=False)

nome = 'Geek University'  # type: str

