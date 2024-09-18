import asyncio


async def running():
    print("Executando antes de dormir runnin")
    await asyncio.sleep(2)
    print("Executando depois  de dormir runnin")


async def running_1():
    print("Executando antes de dormir runnin_1")
    await asyncio.sleep(4)
    print("Executando depois  de dormir runnin_1")


async def running_2():
    print("Executando antes de dormir runnin_2")
    await asyncio.sleep(6)
    print("Executando depois  de dormir runnin_2")


async def main():
    # done, pending = await asyncio.wait([asyncio.create_task(running()), asyncio.create_task(running_1()), asyncio.create_task(running_2())])
    # print(done, pending)
    for coro in asyncio.as_completed([asyncio.create_task(running()), asyncio.create_task(running_1()), asyncio.create_task(running_2())]):
        print(coro)
        await coro


if __name__ == '__main__':
    asyncio.run(main())
