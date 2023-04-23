import asyncio


async def some_coro(param):
    await asyncio.sleep(5)
    print(param)


background_tasks = set()


async def main():
    for i in range(10):
        task = asyncio.create_task(some_coro(param=i))

        # Add task to the set. This creates a strong reference.
        background_tasks.add(task)

        # To prevent keeping references to finished tasks forever,
        # make each task remove its own reference from the set after
        # completion:
        task.add_done_callback(background_tasks.discard)
    
    print("Fazneod algo aqui")


if __name__ == '__main__':
    asyncio.run(main())
    # loop = asyncio.get_running_loop()
    # task_function = asyncio.ensure_future(main())
    # loop.run_forever()
