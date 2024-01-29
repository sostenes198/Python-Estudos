import threading
import time


def contar(oque_e, contador):
    for n in range(1, contador+1):
        print(f'{n} {oque_e}(s)...')
        time.sleep(1)


def main():
    th = threading.Thread(target=contar, args=('elefante', 10))

    th.start()
    
    time.sleep(5)
    print('Podemos fazer outras operações enquanto a thread contar esta executando')
    print('Podemos executar outras coisas')
    
    th.join()
    
    print('Thread finalzada')


if __name__ == '__main__':
    main()
