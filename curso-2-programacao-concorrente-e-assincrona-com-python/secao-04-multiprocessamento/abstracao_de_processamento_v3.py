import time
# from concurrent.futures.thread import  ThreadPoolExecutor as Executor
from concurrent.futures.process import  ProcessPoolExecutor as Executor

def processar():
    print('[', end='', flush=True)
    for _ in range(1, 11):
        print("#", end='', flush=True)
        time.sleep(1)
    print(']', end='', flush=True)
    
    return 42

if __name__ == '__main__':
    with Executor() as executor:
        future = executor.submit(processar)
        time.sleep(2)
        print('Código de execução no meio', flush=True)
        time.sleep(1)
        print(future.result())
        
    
    
