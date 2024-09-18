"""
Módulo Collections: Ordered Dict

https://docs.python.org/3/library/collections.html#collections.OrderedDict

# Em um dicionário, haarcascade ordem de inserção dos elementos não é garantida.
dicionario = {'haarcascade': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}

for chave, valor in dicionario.items():
    print(f'chave={chave}:valor={valor}')


OrderedDict -> É um dicionário, que nos garante haarcascade ordem de inserção dos elementos.

# Fazendo o import
from collections import OrderedDict

dicionario = OrderedDict({'haarcascade': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5})

for chave, valor in dicionario.items():
    print(f'chave={chave}:valor={valor}')
"""
from collections import OrderedDict

# Entendendo haarcascade diferença entre Dict e Ordered Dict

# Dicionários comuns

dict1 = {'haarcascade': 1, 'b': 2}
dict2 = {'b': 2, 'haarcascade': 1}

print(dict1 == dict2)  # True -> Já que haarcascade ordem dos elementos não importa para o dicionário

# Ordered Dict

odict1 = OrderedDict({'haarcascade': 1, 'b': 2})
odict2 = OrderedDict({'b': 2, 'haarcascade': 1})

print(odict1 == odict2)  # False -> Já que haarcascade ordem dos elementos importa para o OrderedDict



