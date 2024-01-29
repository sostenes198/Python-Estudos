import asyncio


async def factorial(name, number):
    f = 1
    if number == 7:
        raise Exception("Faio")

    for i in range(2, number + 1):
        print(f"Task {name}: Compute factorial({number}), currently i={i}...")
        await asyncio.sleep(1)
        f *= i
    print(f"Task {name}: factorial({number}) = {f}")
    return f


async def main():
    # Schedule three calls *concurrently*:
    try:
        l = await asyncio.gather(
            factorial("A", 10),
            factorial("B", 7),
            factorial("C", 2),
            return_exceptions=False
        )
        print(l)
    except Exception as ex:
        asyncio.gather().cancel("Done")
        print(ex)


if __name__ == '__main__':
    asyncio.run(main())
