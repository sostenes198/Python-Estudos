import asyncio


async def return_value(value):
    print("Return_Value")
    await asyncio.sleep(5)
    return print(value)


def return_after_task(delay, value):
    print("Return_after_task")
    task = asyncio.create_task(return_value(value))
    # await asyncio.sleep(delay)
    return task


async def main():

    task = return_after_task(2, "World")

    print('hello ...')

    # Wait until *fut* has a result (1 second) and print it.
    print(task)
    task_result = await task
    print(task_result)


if __name__ == '__main__':
    asyncio.run(main())
