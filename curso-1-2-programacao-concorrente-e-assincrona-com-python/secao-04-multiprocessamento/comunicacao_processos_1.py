import multiprocessing


def ping(conexao):
    conexao.send('Soso')


def pong(conexao):
    msg = conexao.recv()
    print(msg)


def main():
    conn1, conn2 = multiprocessing.Pipe(True)

    p1 = multiprocessing.Process(target=ping, args=(conn1,))
    p2 = multiprocessing.Process(target=pong, args=(conn2,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()


if __name__ == '__main__':
    main()
