import modulos_primeiro_exemplo


def funcao2():
    primeiro.funcao1()


if __name__ == '__main__':
    funcao2()
    print('modulos_segundo_exemplo.py está sendo executado diretamente.')
else:
    print(f'modulos_segundo_exemplo.py foi importado. {__name__}')
