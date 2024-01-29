import asyncio
import time


def blocking_io(value1, value2):
    print("Mostrando valor value1: ", value1)
    time.sleep(2)
    print("Mostrando valor value2: ", value2)


async def main():
    thread = asyncio.create_task(asyncio.to_thread(blocking_io, "Value1_Ola", "Value2_Mundo"))

    print(thread)

    print("Executando main")
    
    await asyncio.sleep(5)
    
    print("Executando após sleep")
    
    print(thread)

    await thread


if __name__ == '__main__':
    asyncio.run(main())
