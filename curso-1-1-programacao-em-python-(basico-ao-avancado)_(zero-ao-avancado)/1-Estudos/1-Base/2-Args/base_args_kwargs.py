"""
**kwargs

Poderíamos chamar este parâmetro de **xis, mas por convenção chamamos de **kwargs

Este é só mais um parâmetro, mas diferente do *args que coloca os valores extras
em uma tupla, o **kwargs exige que utilizemos parâmetros nomeados, e transforma esses
parâmetros extras em um dicionário.

# Exemplo


def cores_favoritas(**kwargs):
    for pessoa, cor in kwargs.items():
        print(f'A cor favorita de {pessoa.title()} é {cor}')


cores_favoritas(marcos='verde', julia='amarelo', fernanda='azul', vanessa='branco')


# OBS: Os parâmetros *args e **kwargs não são obrigatórios.

cores_favoritas()

cores_favoritas(_Geek='navy')

#  Exemplo mais complexo


def cumprimento_especial(**kwargs):
    if '_Geek' in kwargs and kwargs['_Geek'] == 'Python':
        return 'Você recebeu um cumprimento Pythônico Geek!'
    elif '_Geek' in kwargs:
        return f"{kwargs['_Geek']} Geek!"
    return 'Não tenho certeza quem você é ...'


print(cumprimento_especial())
print(cumprimento_especial(_Geek='Python'))
print(cumprimento_especial(_Geek='Oi'))
print(cumprimento_especial(_Geek='especial'))

# Nas nossas funções, podemos ter (NESTA ORDEM):

- Parâmetros obrigatórios;
- *args;
- Parâmetros detault (não obrigatórios);
- **kwargs

def minha_funcao(idade, nome, *args, solteiro=False, **kwargs):
    print(f'{nome} tem {idade} anos')
    print(args)
    if solteiro:
        print('Solteiro')
    else:
        print('Casado')
    print(kwargs)


minha_funcao(8, 'Julia')
minha_funcao(18, 'Felicity', 4, 5, 3, solteiro=True)
minha_funcao(34, 'Felipe', eu='Não', voce='Vai')
minha_funcao(19, 'Carla', 9, 4, 3, java=False, python=True)

# Entenda por quê é importante manter haarcascade ordem dos parâmetros na declaração


# Função com haarcascade ordem correta de parâmetros
#def mostra_info(haarcascade, b, *args, instrutor='Geek', **kwargs):
#    return [haarcascade, b, args, instrutor, kwargs]

# Função com haarcascade ordem incorreta de parâmetros
def mostra_info(haarcascade, b, instrutor='Geek', *args, **kwargs):
    return [haarcascade, b, args, instrutor, kwargs]


haarcascade = 1
b = 2
args = (3,)
instrutor = 'Geek'
kwargs = {'sobrenome': 'University', 'cargo': 'Instrutor'}


print(mostra_info(1, 2, 3, sobrenome='University', cargo='Instrutor'))

# Desempacotar com **kwargs

def mostra_nomes(**kwargs):
    return f"{kwargs['nome']} {kwargs['sobrenome']}"


nomes = {'nome': 'Felicity', 'sobrenome': 'Jones'}

print(mostra_nomes(**nomes))

"""


def soma_multiplos_numeros(a, b, c, **kwargs):
    print(a + b + c)


lista = [1, 2, 3]
tupla = (1, 2, 3)
conjunto = {1, 2, 3}

soma_multiplos_numeros(*lista)
soma_multiplos_numeros(*tupla)
soma_multiplos_numeros(*conjunto)


dicionario = dict(a=1, b=2, c=3)

soma_multiplos_numeros(**dicionario)

# OBS! Os nomes da chave em um dicionário devem ser os mesmos dos parâmetros da função

# dicionario = dict(d=1, e=2, f=3)  # TypeError
# soma_multiplos_numeros(**dicionario)

dicionario = dict(a=1, b=2, c=3, nome='Geek')

soma_multiplos_numeros(**dicionario, lang='Python')
