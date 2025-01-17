import asyncio
import time


async def say_after(delay, what):
    print(what)


async def main():
    func1 = asyncio.create_task(say_after(1, 'hello'))
    func2 = asyncio.create_task(say_after(2, 'world'))

    await asyncio.sleep(4)
    print("Execuntadno coisa no meio")
    await asyncio.sleep(2)

    await func1
    await func2


if __name__ == '__main__':
    asyncio.run(main())
