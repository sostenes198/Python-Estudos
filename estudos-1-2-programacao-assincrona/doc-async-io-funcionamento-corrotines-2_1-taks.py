import asyncio
import time


async def say(what):
    print(what)


def say_after(delay, what):
    print(f"Dentro da função say_after {what}")
    return asyncio.create_task(say(what))


async def main():
    func1 = say_after(1, 'hello')
    func2 = say_after(2, 'world')
    
    print(func1)
    print(func2)

    await asyncio.sleep(2)

    print(func1)
    print(func2)
    
    print("Execuntadno coisa no meio")
    await asyncio.sleep(2)

    await func1
    await func2


if __name__ == '__main__':
    asyncio.run(main())
