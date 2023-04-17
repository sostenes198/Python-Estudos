# O módulo os para interação com o sistema
# Doc: https://docs.python.org/3/library/os.html
# O módulo `os` fornece funções para interagir com o sistema operacional.
# Por exemplo, o módulo os.path contém funções para trabalhar com caminhos de
# arquivos e a função os.listdir() pode ser usada para listar os arquivos em um
# diretório. O método os.system() permite executar comandos do sistema
# operacional a partir do seu código Python.
# Windows 11 (PowerShell), Linux, Mac = clear
# Windows (antigo, cmd) = cls

import os

os.system('cls')
os.system('echo "Hello world"')

print('a' * 80)
print('a' * 80)
print('a' * 80)
print('a' * 80)
print('a' * 80)
print('a' * 80)

# os.path trabalha com caminhos em Windows, Linux e Mac
# Doc: https://docs.python.org/3/library/os.path.html#module-os.path
# os.path é um módulo que fornece funções para trabalhar com caminhos de
# arquivos em Windows, Mac ou Linux sem precisar se preocupar com as diferenças
# entre esses sistemas.
# Exemplos do os.path:
# os.path.join: junta strings em um único caminho. Desse modo,
# os.path.join('pasta1', 'pasta2', 'arquivo.txt') retornaria
# 'pasta1/pasta2/arquivo.txt' no Linux ou Mac, e
# 'pasta1\pasta2\arquivo.txt' no Windows.
# os.path.split: divide um caminho uma tupla (diretório, arquivo).
# Por exemplo, os.path.split('/home/user/arquivo.txt')
# retornaria ('/home/user', 'arquivo.txt').
# os.path.exists: verifica se um caminho especificado existe.
# os.path só trabalha com caminhos de arquivos e não faz nenhuma
# operação de entrada/saída (I/O) com arquivos em si.

caminho = os.path.join('Desktop', 'curso', 'arquivo.txt')
# print(caminho)
diretorio, arquivo = os.path.split(caminho)
nome_arquivo, extensao_arquivo = os.path.splitext(arquivo)
# print(nome_arquivo, extensao_arquivo)
# print(os.path.exists('/Users/luizotavio/Desktop/curso-python-rep'))
# print(os.path.abspath('.'))
print(caminho)
print(os.path.basename(caminho))
print(os.path.basename(diretorio))
print(os.path.dirname(caminho))

# os.listdir para navegar em caminhos
# /Users/luizotavio/Desktop/EXEMPLO
# C:\Users\luizotavio\Desktop\EXEMPLO
# caminho = r'C:\\Users\\luizotavio\\Desktop\\EXEMPLO'

caminho = os.path.join('/Users', 'luizotavio', 'Desktop', 'EXEMPLO')

for pasta in os.listdir(caminho):
    caminho_completo_pasta = os.path.join(caminho, pasta)
    print(pasta)

    if not os.path.isdir(caminho_completo_pasta):
        continue

    for imagem in os.listdir(caminho_completo_pasta):
        print('  ', imagem)

# os.walk para navegar de caminhos de forma recursiva
# os.walk é uma função que permite percorrer uma estrutura de diretórios de
# maneira recursiva. Ela gera uma sequência de tuplas, onde cada tupla possui
# três elementos: o diretório atual (root), uma lista de subdiretórios (dirs)
# e uma lista dos arquivos do diretório atual (files).        
from itertools import count

caminho = os.path.join('/Users', 'luizotavio', 'Desktop', 'EXEMPLO')
counter = count()

for root, dirs, files in os.walk(caminho):
    the_counter = next(counter)
    print(the_counter, 'Pasta atual', root)

    for dir_ in dirs:
        print('  ', the_counter, 'Dir:', dir_)

    for file_ in files:
        caminho_completo_arquivo = os.path.join(root, file_)
        print('  ', the_counter, 'FILE:', caminho_completo_arquivo)
        # NÃO FAÇA ISSO (VAI APAGAR TUDO DA PASTA)
        # os.unlink(caminho_completo_arquivo)

# os.path.getsize e os.stat para dados dos arquivos (tamanho em bytes)        
import math
import os
from itertools import count

def formata_tamanho(tamanho_em_bytes: int, base: int = 1000) -> str:
    """Formata um tamanho, de bytes para o tamanho apropriado"""

    # Original:
    # https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python

    # Se o tamanho for menor ou igual a 0, 0B.
    if tamanho_em_bytes <= 0:
        return "0B"

    # Tupla com os tamanhos
    #                      0    1     2     3     4     5
    abreviacao_tamanhos = "B", "KB", "MB", "GB", "TB", "PB"
    # Logaritmo -> https://brasilescola.uol.com.br/matematica/logaritmo.htm
    # math.log vai retornar o logaritmo do tamanho_em_bytes
    # com a base (1000 por padrão), isso deve bater
    # com o nosso índice na abreviação dos tamanhos
    indice_abreviacao_tamanhos = int(math.log(tamanho_em_bytes, base))
    # Por quanto nosso tamanho deve ser dividido para
    # gerar o tamanho correto.
    potencia = base ** indice_abreviacao_tamanhos
    # Nosso tamanho final
    tamanho_final = tamanho_em_bytes / potencia
    # A abreviação que queremos
    abreviacao_tamanho = abreviacao_tamanhos[indice_abreviacao_tamanhos]
    return f'{tamanho_final:.2f} {abreviacao_tamanho}'


caminho = os.path.join('/Users', 'luizotavio', 'Desktop', 'EXEMPLO')
counter = count()

for root, dirs, files in os.walk(caminho):
    the_counter = next(counter)
    print(the_counter, 'Pasta atual', root)

    for dir_ in dirs:
        print('  ', the_counter, 'Dir:', dir_)

    for file_ in files:
        caminho_completo_arquivo = os.path.join(root, file_)
        # tamanho = os.path.getsize(caminho_completo_arquivo)
        stats = os.stat(caminho_completo_arquivo)
        tamanho = stats.st_size
        print('  ', the_counter, 'FILE:', file_, formata_tamanho(tamanho))
        # NÃO FAÇA ISSO (VAI APAGAR TUDO DA PASTA)
        # os.unlink(caminho_completo_arquivo)

# os + shutil - Copiando arquivos com Python
# Vamos copiar arquivos de uma pasta para outra.
# Copiar -> shutil.copy
import os
import shutil

HOME = os.path.expanduser('~')
DESKTOP = os.path.join(HOME, 'Desktop')
PASTA_ORIGINAL = os.path.join(DESKTOP, 'EXEMPLO')
NOVA_PASTA = os.path.join(DESKTOP, 'NOVA_PASTA')

os.makedirs(NOVA_PASTA, exist_ok=True)

for root, dirs, files in os.walk(PASTA_ORIGINAL):
    for dir_ in dirs:
        caminnho_novo_diretorio = os.path.join(
            root.replace(PASTA_ORIGINAL, NOVA_PASTA), dir_
        )
        os.makedirs(caminnho_novo_diretorio, exist_ok=True)

    for file in files:
        caminho_arquivo = os.path.join(root, file)
        caminnho_novo_arquivo = os.path.join(
            root.replace(PASTA_ORIGINAL, NOVA_PASTA), file
        )
        shutil.copy(caminho_arquivo, caminnho_novo_arquivo)

# os + shutil - Apagando, copiando, movendo e renomeando pastas com Python
# Vamos copiar arquivos de uma pasta para outra.
# Copiar -> shutil.copy
# Copiar Árvore recursivamente -> shutil.copytree
# Apagar Árvore recursivamente -> shutil.rmtree
# Apagar arquivos -> os.unlink
# Renomear/Mover -> shutil.move ou os.rename
import os
import shutil

HOME = os.path.expanduser('~')
DESKTOP = os.path.join(HOME, 'Desktop')
PASTA_ORIGINAL = os.path.join(DESKTOP, 'EXEMPLO')
NOVA_PASTA = os.path.join(DESKTOP, 'NOVA_PASTA')

shutil.rmtree(NOVA_PASTA, ignore_errors=True)
shutil.copytree(PASTA_ORIGINAL, NOVA_PASTA)
# shutil.move(NOVA_PASTA, NOVA_PASTA + '_EITA')
shutil.rmtree(NOVA_PASTA, ignore_errors=True)

# os.makedirs(NOVA_PASTA, exist_ok=True)

# for root, dirs, files in os.walk(PASTA_ORIGINAL):
#     for dir_ in dirs:
#         caminnho_novo_diretorio = os.path.join(
#             root.replace(PASTA_ORIGINAL, NOVA_PASTA), dir_
#         )
#         os.makedirs(caminnho_novo_diretorio, exist_ok=True)

#     for file in files:
#         caminho_arquivo = os.path.join(root, file)
#         caminnho_novo_arquivo = os.path.join(
#             root.replace(PASTA_ORIGINAL, NOVA_PASTA), file
#         )
#         shutil.copy(caminho_arquivo, caminnho_novo_arquivo)