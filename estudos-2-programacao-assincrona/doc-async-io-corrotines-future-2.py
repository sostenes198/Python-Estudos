import asyncio


async def return_after_future(delay, value):
    loop = asyncio.get_running_loop()
    fut = loop.create_future()
    await asyncio.sleep(delay)
    fut.set_result(value)
    return fut

async def return_after_task(delay, value):
    loop = asyncio.get_running_loop()
    fut = loop.create_future()
    await asyncio.sleep(delay)
    fut.set_result(value)
    return fut


async def main():
    
    fut = return_after_future(2, "World")

    print('hello ...')

    # Wait until *fut* has a result (1 second) and print it.
    print((await fut).result())


if __name__ == '__main__':
    asyncio.run(main())
