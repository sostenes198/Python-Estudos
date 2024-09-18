import asyncio


async def diz_oi():
    print('Oi ...')
    

if __name__ == '__main__':
    el = asyncio.get_event_loop()
    el.run_until_complete(diz_oi())
    el.close() 
