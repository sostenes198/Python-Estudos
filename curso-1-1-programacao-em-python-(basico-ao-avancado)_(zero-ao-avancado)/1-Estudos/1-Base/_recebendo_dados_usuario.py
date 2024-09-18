# Entrada de dados
print("Qual é o seu nome?")

nome = input()

print("Seja bem vindo %s" % nome)

print("Qual sua idade: ")
idade = input()

print("%s tem %s anos" % (nome, idade))

# Forma de print mais moderna

print('Seja bem vindo {0}'.format(nome))
print('{0} tem anos {1}'.format(nome, idade))

# Exemplo mais atual

print(f'Seja bem vindo {nome}')
print(f'{nome} tem anos {idade}')
