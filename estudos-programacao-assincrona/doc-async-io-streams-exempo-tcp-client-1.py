import asyncio


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)

    print(f'Client: Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    print(f'Client: Received: {data.decode()!r}')

    print(f'Client: Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    print(f'Client: Received: {data.decode()!r}')

    print('Client: Close the connection')
    writer.close()
    await writer.wait_closed()


if __name__ == '__main__':
    asyncio.run(tcp_echo_client('Hello World!'))
