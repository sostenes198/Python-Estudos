## Links de estudos:

[https://medium.com/@edytarcio/async-await-introdu%C3%A7%C3%A3o-%C3%A0-programa%C3%A7%C3%A3o-ass%C3%ADncrona-em-python-fa30d077018e](https://medium.com/@edytarcio/async-await-introdu%C3%A7%C3%A3o-%C3%A0-programa%C3%A7%C3%A3o-ass%C3%ADncrona-em-python-fa30d077018e)

[https://acervolima.com/corrotina-em-python/](https://acervolima.com/corrotina-em-python/)

[https://docs.python.org/pt-br/3/library/asyncio.html](https://docs.python.org/pt-br/3/library/asyncio.html)

[https://docs.python.org/pt-br/3/library/asyncio-task.html#coroutine](https://docs.python.org/pt-br/3/library/asyncio-task.html#coroutine)
    

# 🐍 Python — Async/Await, Coroutines e Threads

Este documento explica de forma detalhada como funcionam **corrotinas**, **async/await** e **threads** no Python, com exemplos práticos e melhores práticas.

---

## 📌 Conceitos Fundamentais

- **Concorrência ≠ Paralelismo**
  - **Concorrência**: alternância entre tarefas.
  - **Paralelismo**: execução ao mesmo tempo (ex.: múltiplas CPUs).
- **GIL (Global Interpreter Lock)**: no CPython, apenas **uma thread por processo** executa bytecode Python por vez.  
  Threads **não escalam CPU-bound**, mas funcionam bem para I/O-bound.

---

## ⚡ Async/Await e Corrotinas

### O que são Corrotinas?
- Criadas com `async def`.
- Ao chamar, retornam um **coroutine object** (não executam imediatamente).
- São executadas com `await` ou agendadas com `asyncio.create_task`.

### Event Loop
- Gerencia quando cada corrotina é executada.
- Alterna entre tarefas **quando elas fazem `await`** em algo não-bloqueante.

### Exemplo Básico
```python
import asyncio

async def work(name, secs):
    await asyncio.sleep(secs)  # NÃO bloqueia o loop
    return f"{name} done in {secs}s"

async def main():
    t1 = asyncio.create_task(work("A", 1))
    t2 = asyncio.create_task(work("B", 1))
    results = await asyncio.gather(t1, t2)
    print(results)

asyncio.run(main())
