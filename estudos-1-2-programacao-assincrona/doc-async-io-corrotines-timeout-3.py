import asyncio


async def eternity():
    # Sleep for one hour
    await asyncio.sleep(3600)
    print('yay!')


async def main():
    # Wait for at most 1 second
    try:
        await asyncio.wait_for(eternity(), timeout=1.0)
    except TimeoutError:
        print('timeout!')


asyncio.run(main())

# Expected output:
#
#     timeout!

if __name__ == '__main__':
    asyncio.run(main())
