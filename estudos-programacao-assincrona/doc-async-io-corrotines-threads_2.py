import asyncio
import time


def blocking_io(value1, value2):
    print("Mostrando valor value1: ", value1)
    time.sleep(5)
    print("Mostrando valor value2: ", value2)


async def main():
    thread = asyncio.to_thread(blocking_io, "Value1_Ola", "Value2_Mundo")
    
    print(thread)

    print("Executando main")

    await asyncio.sleep(2)
    print("Executando após sleep")
    
    
    await thread


if __name__ == '__main__':
    asyncio.run(main())
