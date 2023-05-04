import asyncio
import aiofiles
import aiohttp
import bs4


async def pegar_links():
    links = []
    async with aiofiles.open('07-02+-+links.txt') as arquivo:
        async for link in arquivo:
            links.append(link.strip())

    return links


async def pegar_html(link):
    print(f'Pegando o HTML do curso {link}')
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            resp.raise_for_status()

            return resp.text()


def pegar_titulo(html):
    soup = bs4.BeautifulSoup(html, ' html.parser')

    title = soup.select_one('title')
    title.text.split('|')[0].strip()

    return title


async def imprimir_titulos():
    links = await pegar_links()
    tarefas = []
    for link in links:
        tarefas.append(asyncio.create_task(pegar_html(link)))

    for tarefa in tarefas:
        html = await tarefa
        titulo = pegar_titulo(html)

        print(f'Curso: {titulo}')


async def main():
    await imprimir_titulos()


if __name__ == '__main__':
    asyncio.run(main())
