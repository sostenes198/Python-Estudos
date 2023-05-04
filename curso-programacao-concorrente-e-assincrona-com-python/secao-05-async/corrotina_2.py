import asyncio


async def diz_oi_demorado():
    print('Oi ...')
    await asyncio.sleep(2)
    print('Todos')
    

if __name__ == '__main__':
    el = asyncio.get_event_loop()
    el.run_until_complete(diz_oi_demorado())
    el.close() 
