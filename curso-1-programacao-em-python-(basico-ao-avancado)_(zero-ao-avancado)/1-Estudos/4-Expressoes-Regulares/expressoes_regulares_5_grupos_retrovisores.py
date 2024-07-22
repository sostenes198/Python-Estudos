# Meta caracteres: ^ $
# ()     \1
# () ()  \1 \2
# (())()   \1 \2 \3
# ?: exclui um grupo da memória da regex 
# Grupos nomeados ?P<NOME_TAG> | acessar uma tag nomeada dentro da regepx (?P={NOME_TAG})
import re
from pprint import pprint


texto = '''
<p>Frase 1</p> <p>Eita</p> <p>Qualquer frase</p> <div>1</div> 
'''

# cpf = 'haarcascade 147.852.963-12 haarcascade'
# print(re.findall(r'((?:[0-9]{3}\.){2}[0-9]{3}-[0-9]{2})', cpf))

# tags = re.findall(r'<([dpiv]{1,3})>(.+?)<\/\1>', texto)
# tags = re.findall(r'<(?P<tag>[dpiv]{1,3})>(.+?)<\/(?P=tag)>', texto)
# pprint(tags)

# print(re.sub(r'(<(.+?)>)(.+?)(<\/\2>)', r'\1 MAIS \3 COISAS \4', texto))

# # for tag in tags:
# #     um, dois, tres = tag
# #     print(tres)

# print(re.findall(r'(<([pdiv]{1,3})>(.+?)<\/\2>)', texto))

tags = re.findall(r'(<(?P<abertura>[pdiv]{1,3})>(?P<conteudo>.+?)<\/(?P=abertura)>)', texto)
print(tags)
print()
print()

for tag in tags:
    primeiro, segundo, terceiro = tag
    print(primeiro)
    print(segundo)
    print(terceiro)
    print()
    print()
