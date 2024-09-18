
def funcao1():
    print('Geek University - modulos_primeiro_exemplo.py')


if __name__ == '__main__':
    funcao1()
    print('modulos_primeiro_exemplo.py está sendo executado diretamente')
else:
    print(f'modulos_primeiro_exemplo.py foi importado. {__name__}')
