import threading
import random
import time

from typing import List


lock = threading.RLock()


class Conta:

    def __init__(self, saldo=0) -> None:
        self.saldo = saldo


def main():
    contas = criar_contas()

    with lock:
        total = sum(conta.saldo for conta in contas)

    print('Iniciando transfêrencias...')

    tarefas = [
        threading.Thread(target=servicos, args=(contas, total,)),
        threading.Thread(target=servicos, args=(contas, total,)),
        threading.Thread(target=servicos, args=(contas, total,)),
        threading.Thread(target=servicos, args=(contas, total,)),
        threading.Thread(target=servicos, args=(contas, total,)),
        threading.Thread(target=servicos, args=(contas, total,)),
    ]

    [tarefa.start() for tarefa in tarefas]
    [tarefa.join() for tarefa in tarefas]

    print('Trasnfêrencias completas.')
    valida_banco(contas, total)


def servicos(contas, total):
    for _ in range(1, 10_000):
        c1, c2 = pega_duas_contas(contas)
        valor = random.randint(1, 100)
        transferir(c1, c2, valor)
        valida_banco(contas, total)


def criar_contas() -> List[Conta]:
    return [
        Conta(saldo=random.randint(5_000, 10_000)),
        Conta(saldo=random.randint(5_000, 10_000)),
        Conta(saldo=random.randint(5_000, 10_000)),
        Conta(saldo=random.randint(5_000, 10_000)),
        Conta(saldo=random.randint(5_000, 10_000)),
        Conta(saldo=random.randint(5_000, 10_000)),
        Conta(saldo=random.randint(5_000, 10_000)),
        Conta(saldo=random.randint(5_000, 10_000)),
        Conta(saldo=random.randint(5_000, 10_000)),
        Conta(saldo=random.randint(5_000, 10_000)),
    ]


def transferir(origem: Conta, destino: Conta, valor: int) -> None:
    if origem.saldo < valor:
        return

    with lock:
        origem.saldo -= valor
        time.sleep(0.0001)
        destino.saldo += valor


def valida_banco(contas: List[Conta], total: int) -> None:
    with lock:
        atual = sum(conta.saldo for conta in contas)
        
    if atual != total:
        print(f'Erro: Balanço bancário inconsistente. BRL$ {atual:.2f} vs {total:.2f}', flush=True)
    else:
        print(f'Tudo certo: Balanço bancário consistente BRL$ {total:.2f}', flush=True)


def pega_duas_contas(contas: List[Conta]) -> tuple[Conta, Conta]:
    c1 = random.choice(contas)
    c2 = random.choice(contas)

    while c1 == c2:
        c2 = random.choice(contas)

    return c1, c2


if __name__ == '__main__':
    main()
