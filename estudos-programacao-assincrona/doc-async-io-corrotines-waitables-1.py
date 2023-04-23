import asyncio


async def nested_coroutine():
    print('nested_coroutine')
    return 42


async def return_42():
    print('return_42')
    return 42


async def nested_task():
    # return asyncio.create_task(return_42())
    print('nested_task')
    return return_42()

async def main():
    # Nothing happens if we just call "nested()".
    # A coroutine object is created but not awaited,
    # so it *won't run at all*.
    coroutine = nested_coroutine()
    task = asyncio.create_task(nested_task())

    # Let's do it differently now and await it:
    print(coroutine)
    print(task)
    print(await nested_coroutine())  # will print "42".


if __name__ == '__main__':
    asyncio.run(main())
