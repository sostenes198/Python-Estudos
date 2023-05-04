import multiprocessing
import time


def funcao_1(val, stat):
    if stat:
        res = val + 10
        stat = False
    else:
        res = val + 20
        val = 100
        stat = True

    print(f'O resultado da função 1 é {res}')
    time.sleep(0.001)


def funcao_2(val, stat):
    if stat:
        res = val + 30
        stat = False
    else:
        res = val + 40
        val = 400
        stat = True

    print(f'O resultado da função 2 é {res}')
    time.sleep(0.001)


def main():
    valor = 100
    status = False

    p1 = multiprocessing.Process(target=funcao_1, args=(valor, status,))
    p2 = multiprocessing.Process(target=funcao_2, args=(valor, status,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()


if __name__ == '__main__':
    main()
