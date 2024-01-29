import asyncio


async def long_running_task():
    await asyncio.sleep(5)


async def main():
    try:
        async with asyncio.timeout(2):
            await long_running_task()
    except TimeoutError:
        print("The long operation timed out, but we've handled it.")

    print("This statement will run regardless.")

if __name__ == '__main__':
    asyncio.run(main())