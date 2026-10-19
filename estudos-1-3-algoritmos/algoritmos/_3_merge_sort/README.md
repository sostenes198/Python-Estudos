# Ordenação por intercalação (MERGE-SORT)

Esta pasta tem duas implementações do mesmo algoritmo:

| Arquivo | O que é |
|---|---|
| [`merge_sort.py`](merge_sort.py) | A versão do livro (Cormen et al.), recursiva, que usa o [`merge`](../_2_merge/README.md) |
| [`merge_sort_parallel.py`](merge_sort_parallel.py) | A versão avançada, otimizada e com threads, independente da primeira |
| [`benchmark.py`](benchmark.py) | Compara as duas e o `list.sort()` do Python |

## Como executar

Os arquivos se importam pelo nome do pacote (`algoritmos...`), então o Python precisa enxergar a **raiz do projeto**. A forma mais simples é rodar com `-m` a partir dela:

```
python -m algoritmos._3_merge_sort.merge_sort
python -m algoritmos._3_merge_sort.merge_sort_parallel
python -m algoritmos._3_merge_sort.benchmark
```

No VS Code, a configuração **Python: arquivo atual** do `launch.json` já define `PYTHONPATH` como a raiz do projeto, então o botão de executar funciona direto.

Rodar `python merge_sort.py` de dentro da pasta, sem `PYTHONPATH`, falha com `ModuleNotFoundError: No module named 'algoritmos'`.

---

# Parte 1: `merge_sort.py` (a versão do livro)

## A ideia

O merge sort usa **dividir e conquistar**:

1. **Dividir:** parte o trecho `A[p..r]` ao meio.
2. **Conquistar:** ordena cada metade, chamando a si mesmo.
3. **Combinar:** junta as duas metades já ordenadas com o `merge`.

O truque é que um trecho com **zero ou um elemento já está ordenado**. A recursão vai partindo o vetor até chegar nesses pedaços, e daí em diante só o `merge` trabalha, juntando pedaços ordenados cada vez maiores.

```
[5, 2, 4, 7, 1, 3, 2, 6]
 ├── [5, 2, 4, 7]
 │    ├── [5, 2]  →  [5] [2]  →  merge  →  [2, 5]
 │    └── [4, 7]  →  [4] [7]  →  merge  →  [4, 7]
 │                               merge  →  [2, 4, 5, 7]
 └── [1, 3, 2, 6]
      ├── [1, 3]  →  [1] [3]  →  merge  →  [1, 3]
      └── [2, 6]  →  [2] [6]  →  merge  →  [2, 6]
                                 merge  →  [1, 2, 3, 6]
                                 merge  →  [1, 2, 2, 3, 4, 5, 6, 7]
```

## O código

```python
from algoritmos._2_merge.merge import merge


def merge_sort(A, p, r):
    if p >= r:
        return A

    q = (p + r) // 2

    merge_sort(A, p, q)
    merge_sort(A, q + 1, r)

    merge(A, p, q, r)

    return A
```

Segue o pseudocódigo `MERGE-SORT(A, p, r)` do livro (Cormen et al., *Algoritmos*).

### 1. O caso base: `if p >= r`

Se `p == r`, o trecho tem um elemento. Se `p > r`, está vazio. Nos dois casos já está ordenado, então a função volta sem fazer nada. Sem esse teste a recursão nunca pararia.

### 2. O ponto médio: `q = (p + r) // 2`

`//` é a divisão inteira, o equivalente do ⌊(p + r) / 2⌋ do livro. Os limites são **inclusivos**, como no `merge`:

- esquerda: `A[p..q]`
- direita: `A[q+1..r]`

Com um número ímpar de elementos, a esquerda fica com um a mais. Para `A[0..4]` (5 elementos), `q = 2`, então a esquerda tem 3 e a direita tem 2.

### 3. As duas chamadas recursivas

```python
merge_sort(A, p, q)
merge_sort(A, q + 1, r)
```

Cada metade é ordenada no próprio `A`, sem criar cópias. Quando as duas voltam, `A[p..q]` e `A[q+1..r]` estão ordenados, que é exatamente a pré-condição do `merge`.

### 4. A intercalação: `merge(A, p, q, r)`

Junta as duas metades e deixa `A[p..r]` ordenado. Toda a "ordenação" acontece aqui.

### 5. A importação

```python
from algoritmos._2_merge.merge import merge
```

É um import comum, por nome de pacote:

- `algoritmos` e cada subpasta têm um `__init__.py`, o que as torna pacotes importáveis.
- As pastas começam com `_` (`_1_insertion_sort`, `_2_merge`, `_3_merge_sort`) porque um nome de pasta que começa com dígito não é um identificador válido, e `from algoritmos.2_merge...` seria um erro de sintaxe. O `_` mantém a ordem 1, 2, 3 e deixa a pasta importável.
- O import começa em `algoritmos`, então a raiz do projeto precisa estar no caminho de busca do Python. Veja **Como executar**, no começo.

## Exemplo completo

`A = [5, 2, 4, 7, 1, 3, 2, 6]`, chamado com `merge_sort(A, 0, 7)`.

Cada linha é uma chamada ao `merge`, na ordem em que acontecem:

| Chamada | Trecho antes | Trecho depois | `A` inteiro depois |
|---|---|---|---|
| `merge(A, 0, 0, 1)` | `[5, 2]` | `[2, 5]` | `[2, 5, 4, 7, 1, 3, 2, 6]` |
| `merge(A, 2, 2, 3)` | `[4, 7]` | `[4, 7]` | `[2, 5, 4, 7, 1, 3, 2, 6]` |
| `merge(A, 0, 1, 3)` | `[2, 5, 4, 7]` | `[2, 4, 5, 7]` | `[2, 4, 5, 7, 1, 3, 2, 6]` |
| `merge(A, 4, 4, 5)` | `[1, 3]` | `[1, 3]` | `[2, 4, 5, 7, 1, 3, 2, 6]` |
| `merge(A, 6, 6, 7)` | `[2, 6]` | `[2, 6]` | `[2, 4, 5, 7, 1, 3, 2, 6]` |
| `merge(A, 4, 5, 7)` | `[1, 3, 2, 6]` | `[1, 2, 3, 6]` | `[2, 4, 5, 7, 1, 2, 3, 6]` |
| `merge(A, 0, 3, 7)` | `[2, 4, 5, 7, 1, 2, 3, 6]` | `[1, 2, 2, 3, 4, 5, 6, 7]` | `[1, 2, 2, 3, 4, 5, 6, 7]` |

Repare em dois pontos:

- **A recursão desce primeiro:** o primeiro `merge` só acontece depois que a chamada chegou até os pedaços de um elemento. Por isso o primeiro a rodar é `merge(A, 0, 0, 1)`, o par mais à esquerda.
- **Os `merge` são sempre sobre pedaços vizinhos:** cada um junta um trecho já ordenado com o trecho ordenado logo ao lado.

## Exemplo com tamanho ímpar

`A = [9, 4, 7, 1, 8]`, `merge_sort(A, 0, 4)`. Aqui `q = 2`, então a esquerda é `[9, 4, 7]` e a direita é `[1, 8]`.

| Chamada | Trecho antes | Trecho depois |
|---|---|---|
| `merge(A, 0, 0, 1)` | `[9, 4]` | `[4, 9]` |
| `merge(A, 0, 1, 2)` | `[4, 9, 7]` | `[4, 7, 9]` |
| `merge(A, 3, 3, 4)` | `[1, 8]` | `[1, 8]` |
| `merge(A, 0, 2, 4)` | `[4, 7, 9, 1, 8]` | `[1, 4, 7, 8, 9]` |

## Complexidade

- **Tempo, Θ(n log n) em todos os casos.** Vale para o melhor, o médio e o pior cenário do `main`.
  - **Altura da recursão:** o vetor é dividido ao meio a cada nível, então são cerca de `log₂ n` níveis.
  - **Trabalho por nível:** em cada nível, os `merge` juntos tocam os `n` elementos uma vez, e isso custa Θ(n).
  - **Total:** `n × log n`, o que dá a recorrência `T(n) = 2·T(n/2) + Θ(n)`.
- **Número de `merge`:** sempre `n - 1`. Com 8 elementos são 7, como na tabela.
- **Espaço, Θ(n).** Cada `merge` cria cópias `L` e `R` do trecho que está juntando, e a pilha de recursão tem altura de `log n`.
- **Estável:** como o `merge` usa `<=`, elementos iguais mantêm a ordem original. No exemplo, os dois `2` saem na mesma ordem relativa em que entraram.

## Comparando com a ordenação por inserção

| | Inserção | Merge sort |
|---|---|---|
| Melhor caso | Θ(n) | Θ(n log n) |
| Pior caso | Θ(n²) | Θ(n log n) |
| Memória extra | Θ(1) | Θ(n) |
| Estável | sim | sim |

O merge sort não tem um pior caso quadrático, e em troca gasta memória extra e não aproveita vetores já ordenados. Para vetores grandes e desordenados ele ganha de longe. Para vetores pequenos ou quase ordenados, a inserção costuma ser mais rápida, por causa do custo menor por passo.

---

# Parte 2: `merge_sort_parallel.py` (a versão avançada)

Esta versão **não** usa o `merge` e o `merge_sort` da Parte 1. Ela reescreve o algoritmo pensando em velocidade e em threads, e por isso foge do pseudocódigo do livro. A lógica continua sendo a do merge sort: dividir, ordenar as partes e intercalar.

Em vez de `merge_sort(A, p, r)`, a função é `merge_sort_parallel(A, workers=None, parallel_cutoff=PARALLEL_CUTOFF)`. Ela ordena `A` inteiro, no lugar, e devolve `A`.

## O que esperar das threads em Python

Leia isto antes dos números, porque muda a expectativa.

O Python padrão tem o **GIL** (*Global Interpreter Lock*): só **uma thread por vez** executa código Python, mesmo com vários núcleos. Ordenar em Python puro é só código Python, então com o GIL ligado as threads se revezam em vez de trabalhar juntas, e **não há ganho de velocidade**.

O ganho só aparece em um Python **free-threaded** (sem GIL), disponível como build separado a partir do 3.13 (`python3.14t`). Este código foi escrito para escalar nesse caso, mas o Python usado aqui tem o GIL ligado, então **esse ganho não foi medido**.

Por isso o `workers=None` (padrão) escolhe sozinho:

- **GIL ligado:** usa 1 worker, o caminho sequencial.
- **GIL desligado:** usa `os.cpu_count()` threads.

Você pode forçar com `merge_sort_parallel(A, workers=8)`, que é o que o `main` e o benchmark fazem.

## A ideia

```
A = [ ........................... n elementos ........................... ]

Fase 1: corta em `workers` pedaços e ordena cada um em uma thread
        [ pedaço 0 ][ pedaço 1 ][ pedaço 2 ][ pedaço 3 ]
          thread 1    thread 2    thread 3    thread 4
          ordenado    ordenado    ordenado    ordenado

Fase 2: intercala os pedaços dois a dois, nível por nível
        [ 0 + 1 ][ 2 + 3 ]   →   [ 0 + 1 + 2 + 3 ]
```

O problema da fase 2 é que o último `merge` toca o vetor inteiro. Se ele rodar em uma thread só, as outras ficam paradas esperando e o ganho some. A solução é cortar **cada intercalação em pedaços independentes**, com uma busca binária (`_co_rank`, explicada abaixo).

## Passo a passo do código

### 1. Ordenação binária por inserção, para os pedaços pequenos

```python
def _binary_insertion_sort(a):
    for i in range(1, len(a)):
        x = a[i]
        pos = bisect_right(a, x, 0, i)
        if pos != i:
            a[pos + 1 : i + 1] = a[pos:i]
            a[pos] = x
    return a
```

É a ordenação por inserção da pasta `_1_insertion_sort`, com dois ajustes:

- **Busca binária:** o `bisect_right` acha a posição em `O(log n)`, em vez de andar um por um.
- **Deslocamento em bloco:** a atribuição `a[pos+1 : i+1] = a[pos:i]` empurra todos os elementos de uma vez, em C.

Com `a = [3, 1, 2]`:

- **`i = 1`:** `x = 1`, `pos = 0`. Desloca para `[3, 3, 2]` e coloca `a[0] = 1`, ficando `[1, 3, 2]`.
- **`i = 2`:** `x = 2`, `pos = 1`. Desloca para `[1, 3, 3]` e coloca `a[1] = 2`, ficando `[1, 2, 3]`.

A recursão só desce até pedaços de `INSERTION_CUTOFF = 48` elementos. Abaixo disso a inserção é mais rápida do que continuar recursando.

### 2. O `_merge`, que devolve uma lista nova

```python
def _merge(a, i, i_end, b, j, j_end): ...
```

Intercala `a[i:i_end]` e `b[j:j_end]`, já ordenados, em uma **lista nova**. Diferenças em relação ao `merge` da pasta `_2_merge`:

- **Atalhos antes do laço:**
  - Se um dos lados está vazio, devolve o outro.
  - Se `a[i_end-1] <= b[j]`, tudo de `a` vem antes de `b`, então devolve a concatenação. Isso custa `O(1)` de comparações mais uma cópia em C.
  - Se `b[j_end-1] < a[i]`, é o caso inverso.
- **Laço enxuto:** só relê da lista que acabou de avançar, em vez de ler `L[i]` e `R[j]` a cada volta, e usa `append` em vez de índice.
- **Sobra em bloco:** quando um lado acaba, copia o resto do outro com uma fatia, sem laço.
- **Estável:** em empate (`x <= y`), o elemento de `a` sai primeiro.

Esses atalhos explicam por que o vetor já ordenado é tão rápido no benchmark: todas as intercalações viram uma concatenação.

### 3. O `_sort`, que não escreve em lugar nenhum

```python
def _sort(a, lo, hi):
    if hi - lo <= INSERTION_CUTOFF:
        return _binary_insertion_sort(a[lo:hi])
    mid = (lo + hi) // 2
    left = _sort(a, lo, mid)
    right = _sort(a, mid, hi)
    return _merge(left, 0, len(left), right, 0, len(right))
```

É o `merge_sort` da Parte 1, mas **devolve uma lista nova** e só **lê** de `a`. Como nenhuma thread escreve em dados compartilhados, não há travas nem condições de corrida: cada thread recebe seu intervalo `[lo, hi)` e devolve a própria lista.

### 4. O `_co_rank`, que corta um merge em pedaços

A pergunta: **entre os primeiros `k` elementos de `merge(a, b)`, quantos vêm de `a`?** A resposta (`i`) diz onde cortar `a` e `b` (`b` é cortado em `k - i`), e as duas metades passam a ser independentes.

Exemplo com `a = [1, 3, 5, 7]`, `b = [2, 4, 6, 8]` e `k = 4`:

- O resultado completo é `[1, 2, 3, 4, 5, 6, 7, 8]`, e os 4 primeiros são `1, 2, 3, 4`.
- Desses, `1` e `3` vêm de `a`, então `i = 2` e `j = 4 - 2 = 2`.
- A busca binária chega nisso em `O(log n)`:
  - Ela testa `i = 2` (e `j = 2`): `a[2] = 5 <= b[1] = 4`? Não. Então `i` pode ser menor ou igual a 2.
  - Ela testa `i = 1` (e `j = 3`): `a[1] = 3 <= b[2] = 6`? Sim. Então `i` precisa ser maior que 1.
  - O resultado é `i = 2`.

Com o corte em `(2, 2)`, duas threads trabalham ao mesmo tempo, e as saídas se concatenam em ordem:

- **Thread 1:** `merge(a[0:2], b[0:2])` → `[1, 2, 3, 4]`.
- **Thread 2:** `merge(a[2:4], b[2:4])` → `[5, 6, 7, 8]`.

Os empates vão para `a`, igual ao `_merge`. Isso mantém a ordenação estável mesmo cortada em pedaços. Por exemplo, com `a = [2, 2]`, `b = [2]` e `k = 1`, o resultado é `i = 1`: o primeiro elemento da saída vem de `a`.

### 5. O `merge_sort_parallel`

```python
bounds = [n * t // workers for t in range(workers + 1)]
```

Com `n = 20` e `workers = 4`, os cortes são `[0, 5, 10, 15, 20]`. Isso aceita qualquer `n` e qualquer número de workers, sem exigir potência de 2.

Depois:

1. **Ordena os pedaços.** Uma tarefa `_sort(A, lo, hi)` por pedaço, no `ThreadPoolExecutor`. O `.result()` espera todas.
2. **Intercala nível por nível.** Em cada nível, pares de pedaços vizinhos viram um `_split_merge` cada, com `parts = workers // pares` pedaços por par. Assim o número de tarefas fica sempre perto do número de threads:
   - Com 4 workers: o nível 1 tem 2 pares × 2 pedaços = 4 tarefas, e o nível 2 tem 1 par × 4 pedaços = 4 tarefas.
   - Com 3 workers: o primeiro nível intercala o par 0+1 em 3 pedaços, e o pedaço 2, sem par, sobe para o nível seguinte sem ser tocado.
3. **Copia o resultado de volta:** `A[:] = runs[0]`, para que `A` seja ordenado no lugar, como nas outras versões.

Todas as tarefas são enviadas pela **thread principal**, nível por nível. Nenhuma tarefa espera por outra dentro do pool, então não há risco de deadlock.

Como os pedaços são vizinhos e os empates vão para o da esquerda, a ordenação inteira é **estável**.

Vetores com menos de `PARALLEL_CUTOFF = 32768` elementos (ou com menos de `2 × workers`) nem usam threads: criar o pool custaria mais do que ordenar. O `main` passa `parallel_cutoff=0` para forçar o caminho com threads em vetores pequenos, só para demonstrar.

## Otimizações, resumidas

| Técnica | O que ganha |
|---|---|
| Ordenação binária por inserção até 48 elementos | Menos níveis de recursão, e `bisect` + fatias rodam em C |
| `_merge` com atalhos de ordem | Entrada já ordenada ou invertida vira concatenação |
| Laço do `_merge` que só relê um lado | Menos acessos a lista por elemento |
| Sobra copiada em bloco | Sem laço Python no final do `merge` |
| `_sort` sem escrita compartilhada | Sem trava, e vale para free-threaded |
| `_co_rank` | Mesmo o último `merge` usa todas as threads |
| `PARALLEL_CUTOFF = 32768` | Vetores pequenos não pagam o custo de criar threads |

## Complexidade

Com `n` elementos e `p` workers:

- **Trabalho total:** Θ(n log n), o mesmo do merge sort comum.
- **Tempo com `p` núcleos reais:** cerca de Θ((n / p) · log n):
  - A fase 1 ordena pedaços de `n / p` elementos, o que custa `(n / p) · log(n / p)`.
  - A fase 2 tem `log p` níveis, e cada nível divide seu trabalho `n` entre `p` threads, o que custa `(n / p) · log p`.
  - Cada `_co_rank` custa só `O(log n)` e é desprezível.
- **Espaço, Θ(n):** as listas intermediárias são novas, então há cópias extras além de `A`.
- **Estável:** sim.

---

# Comparando as duas versões

Resultados do `benchmark.py`: Python 3.14.6 **com GIL**, 14 CPUs, `n = 200.000`, melhor de 3 execuções. A porcentagem de aceleração é em relação ao `merge_sort` da Parte 1.

| Entrada | `merge_sort` (Parte 1) | Paralelo, 1 thread | Paralelo, 14 threads | `list.sort()` |
|---|---|---|---|---|
| Aleatória | 263 ms | 119 ms (2,2x) | 121 ms (2,2x) | 18,5 ms (14x) |
| Já ordenada | 217 ms | 16 ms (13x) | 18 ms (12x) | 0,2 ms |
| Ordem inversa | 214 ms | 39 ms (5,6x) | 38 ms (5,6x) | 0,3 ms |
| Poucos valores distintos | 232 ms | 83 ms (2,8x) | 84 ms (2,8x) | 8,1 ms (29x) |

O que isso mostra:

- **A versão avançada é bem mais rápida que a do livro,** de 2,2x a 13x, mas por causa das otimizações de código e **não** das threads.
- **As threads não ajudam com o GIL ligado.** 1 thread e 14 threads têm o mesmo tempo, o que confirma que elas se revezam. Também não prejudicam: o custo de criá-las é desprezível a esse tamanho.
- **`list.sort()` é imbatível.** É o Timsort escrito em C, e fica de 6x a 100x na frente de qualquer merge sort escrito em Python. Em código de verdade, use ele. Estes arquivos existem para estudar o algoritmo.

Os tempos variam de máquina para máquina. Rode `python -m algoritmos._3_merge_sort.benchmark` para ver os seus.

## Como ver as threads funcionando de verdade

É preciso um Python free-threaded. Por exemplo, com o pyenv:

```
pyenv install 3.14t
PYENV_VERSION=3.14t python -m algoritmos._3_merge_sort.benchmark
```

A primeira linha do benchmark mostra se o GIL está ativo (`GIL ativo: False` é o que você quer ver). Nesse caso, o esperado é que as linhas com mais threads fiquem mais rápidas que a de 1 thread, mas sem ganho linear perfeito, por motivos como:

- **Cópias em C:** a concatenação das saídas (`out += f.result()`) roda na thread principal e é sequencial.
- **Memória:** a largura de banda de memória é compartilhada entre os núcleos.
- **Coleta de lixo:** cada thread aloca muitas listas pequenas.

Isso é o que se espera pelo desenho, **não** um resultado medido aqui.

Para ganhar velocidade com o GIL ligado, a saída usual é `multiprocessing`, que usa processos em vez de threads. O custo é copiar os dados entre processos, e para ordenar inteiros isso costuma comer boa parte do ganho.
