# def cumprimentar(nome: str) -> str:
#     return f'Olá, {nome}'
#
#
# print(cumprimentar('Geek'))


def cabecalho(texto: str, alinhamento: bool = True) -> str:
    if alinhamento:
        return f"{texto.title()}\n{'-' * len(texto)}"
    else:
        return f" {texto.title()} ".center(50, '#')


print(cabecalho('_Geek university'))

print(cabecalho('_Geek university', alinhamento=False))


print(cabecalho('_Geek university', alinhamento='_Geek'))
