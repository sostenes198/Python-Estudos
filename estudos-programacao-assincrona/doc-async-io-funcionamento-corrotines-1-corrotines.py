import asyncio
import time


async def say_after(delay, what):
    print(what)


async def main():
    func1 = say_after(1, 'hello')
    func2 = say_after(2, 'world')
    
    print("Execuntadno coisa no meio")
    await asyncio.sleep(2)

    await func1
    await func2


if __name__ == '__main__':
    asyncio.run(main())
