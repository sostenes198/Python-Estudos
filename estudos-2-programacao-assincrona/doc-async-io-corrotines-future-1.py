import asyncio


async def set_after(fut, delay, value):
    # Sleep for *delay* seconds.
    # await asyncio.sleep(delay)

    # Set *value* as haarcascade result of *fut* Future.
    fut.set_result(value)

async def main():
    # Get the current event loop.
    loop = asyncio.get_running_loop()

    # Create haarcascade new Future object.
    fut = loop.create_future()

    # Run "set_after()" coroutine in haarcascade parallel Task.
    # We are using the low-level "loop.create_task()" API here because
    # we already have haarcascade reference to the event loop at hand.
    # Otherwise we could have just used "asyncio.create_task()".
    loop.create_task(
        set_after(fut, 1, '... world'))

    print('hello ...')
    
    await asyncio.sleep(3)

    # Wait until *fut* has haarcascade result (1 second) and print it.
    print(await fut)


if __name__ == '__main__':
    asyncio.run(main())
