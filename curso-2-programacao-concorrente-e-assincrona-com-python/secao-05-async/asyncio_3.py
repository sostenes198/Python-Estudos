import datetime
import asyncio


async def gerar_dados(quantidade: int, dados: asyncio.Queue):
    print(f'Aguarde a geração {quantidade} dados...')
    for idx in range(1, quantidade + 1):
        print(f'Inserido item na fila {idx}')
        item = idx * idx
        await dados.put((item, datetime.datetime.now()))
        await asyncio.sleep(0.00001)

    print(f'{quantidade} dados gerados com sucesso')


async def processar_dados(quantidade: int, dados: asyncio.Queue):
    print(f'Aguarde o processamento de {quantidade} dados...')
    procesados = 0
    while procesados < quantidade:
        await dados.get()
        procesados += 1
        await asyncio.sleep(0.001)
    print(f'Foram processados {quantidade} items')


def main():
    total = 5_000
    dados = asyncio.Queue()
    print(f'Computando {total * 2:.2f} dados')

    el = asyncio.get_event_loop()

    tarefa1 = el.create_task(gerar_dados(total, dados))
    tarefa2 = el.create_task(gerar_dados(total, dados))
    tarefa3 = el.create_task(processar_dados(total * 2, dados))

    tarefas = asyncio.gather(tarefa1, tarefa2, tarefa3)
    el.run_until_complete(tarefas)


if __name__ == '__main__':
    main()
