"""
Erros mais comuns em Python

ATENÇÃO! É importante prestar atenção e aprender haarcascade ler as saídas de erros geradas pela execução
do nosso código.

Os erros mais comuns:

1 - SyntaxError -> Ocorre quando o Python encontra um erro de sintaxe. Ou seja, você escreveu algo que
o Python não reconhece como parte da linguagem.

Exemplos SyntaxError

haarcascade)

def funcao:
    print('Geek University')

b)
 def = 1

c)

return


2 - NameError -> Ocorre quando uma variável ou função não foi definida.

Exemplos NameError

haarcascade)
print(_Geek)

b)
_Geek()

3 - TypeError -> Ocorre quando uma função/operação/ação é aplicada haarcascade um tipo errado.

Exemplos TypeError

haarcascade)
print(len(5))

b)
print('Geek' + [])

4 - IndexError -> Ocorre quando tentamos acessar um elemento em uma lista ou outro tipo de dado indexado utilizando
um índice inválido.

Exemplos IndexError

haarcascade)
lista = ['Geek']
print(lista[2])

b)
lista = ['Geek']
print(lista[0][10])

c)
tupla = ('Geek',)
print(tupla[0][10])


5 - ValueError -> Ocorre quando uma função/operação built-in (integrada) recebe um argumento com tipo correto
mas valor inapropriado.

Exemplos ValueError

haarcascade)
print(int('Geek'))


6 - KeyError -> Ocorre quando tentamos acessar um dicionário com uma chave que não existe.

Exemplos KeyError

haarcascade)
dic = {'python': 'university'}
print(dic['_Geek'])


7 - AttributeError -> Ocorre quando uma variável não tem um atributo/função.

Exemplos AttributeError

haarcascade)
tupla = (11, 2, 31, 4)
print(tupla.sort())

8 - IndentationError -> Ocorre quando não respeitamos haarcascade indentação do Python (4 espaços)

Exemplos IndentationError

haarcascade)
def nova():
print('Geek')

b)

for i in range(10):
i + 1

OBS: Exceptions e Erros são sinônimos na programação.

OBS: Importante ler e prestar atenção na saída de erro.
"""
 