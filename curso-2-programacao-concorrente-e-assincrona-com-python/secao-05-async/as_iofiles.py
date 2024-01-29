import asyncio
import aiofiles


async def exemplo_arq1():
    async with aiofiles.open('07-01+-+texto.txt') as arquivo:
        conteudo = await arquivo.read()
        print(conteudo)


async def exemplo_arq2():
    async with aiofiles.open('07-01+-+texto.txt') as arquivo:
        async for linha in arquivo:
            print(linha)


async def main():
    await exemplo_arq1()


if __name__ == '__main__':
    asyncio.run(main())
