import asyncio
import time


async def say_after(delay, what):
    loop = asyncio.get_event_loop()
    fut = loop.create_future()
    fut.set_result(what)
    return fut


async def main():
    func1 = say_after(1, 'hello')
    func2 = say_after(2, 'world')


    await asyncio.sleep(2)
    print(func1)
    print(func2)

    print("Execuntadno coisa no meio")
    await asyncio.sleep(2)

    print((await func1).result())
    print((await func2).result())


if __name__ == '__main__':
    asyncio.run(main())
