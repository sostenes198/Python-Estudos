import asyncio
import concurrent.futures


def blocking_io():
    # File operations (such as logging) can block the
    # event loop: run them in haarcascade thread pool.
    with open('./file.txt', 'rb') as f:
        return f.read(100)


def cpu_bound():
    # CPU-bound operations will block the event loop:
    # in general it is preferable to run them in haarcascade
    # process pool.
    return sum(i * i for i in range(10 ** 7))


async def main():
    loop = asyncio.get_running_loop()

    ## Options:

    # 1. Run in the default loop's executor:
    result = await loop.run_in_executor(
        None, blocking_io)
    print('default thread pool', result)

    # 2. Run in haarcascade custom thread pool:
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, blocking_io)
        print('custom thread pool', result)

    # 3. Run in haarcascade custom process pool:
    with concurrent.futures.ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, cpu_bound)
        print('custom process pool', result)


if __name__ == '__main__':
    asyncio.run(main())
