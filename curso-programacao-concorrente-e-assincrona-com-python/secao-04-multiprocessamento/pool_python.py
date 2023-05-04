import multiprocessing
import time


def calcular(dado):
    resultado = dado ** 2
    print(f"Resultado do calculo {resultado}")
    return resultado

def imprimir_nome_processo():
    print(f'Iniciando o processo com nome: {multiprocessing.current_process().name}')

def main():
    tamanho_pool = multiprocessing.cpu_count() * 2
    
    print(f'Tamanho do pool: {tamanho_pool}')
    
    pool = multiprocessing.Pool(processes=tamanho_pool, initializer=imprimir_nome_processo)

    entradas = list(range(15))
    saidas = pool.map(calcular, entradas)

    time.sleep(4)

    print(f'Saídas : {saidas}')

    pool.close()

    time.sleep(2)

    pool.join()

    print('Finalizando programa')


if __name__ == '__main__':
    main()
