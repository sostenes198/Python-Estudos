# Ordenação por inserção (INSERTION-SORT)

Implementação em [`insertion_sort.py`](insertion_sort.py).

## A ideia

É o mesmo método de ordenar cartas de baralho na mão. Você segura as cartas já ordenadas na mão esquerda, pega a próxima carta com a direita e a encaixa no lugar certo entre as que já estão ordenadas.

No vetor, o lado esquerdo é a parte ordenada e o direito é a parte ainda não vista:

```
        ordenado     |  ainda não visto
A = [ 2, 4, 5, 6 ]   |  [ 1, 3 ]
                  ^
                  i (próximo a encaixar)
```

A cada volta, o elemento `A[i]` é encaixado na parte ordenada à esquerda dele, e a parte ordenada cresce em um elemento.

## Passo a passo do código

```python
def insertion_sort(A, n):
    for i in range(1, n):
        key = A[i]
        j = i - 1
        while j >= 0 and A[j] > key:
            A[j + 1] = A[j]
            j = j - 1
        A[j + 1] = key
    return A
```

### 1. O laço externo: `for i in range(1, n)`

- Começa em `i = 1`, não em 0. Um subvetor de um elemento (`A[0]`) já está ordenado, então não há nada a encaixar nele.
- `n` é o número de elementos a ordenar. Normalmente é `len(A)`.
- A cada `i`, o objetivo é encaixar `A[i]` entre `A[0..i-1]`.

### 2. Guardar a chave: `key = A[i]`

O elemento que será encaixado precisa ser salvo, porque a posição `A[i]` vai ser sobrescrita logo em seguida, durante o deslocamento dos elementos maiores.

### 3. O ponteiro de busca: `j = i - 1`

`j` começa no último elemento da parte ordenada, ou seja, o vizinho da esquerda de `key`, e anda para a esquerda procurando o lugar de `key`.

### 4. O laço interno: `while j >= 0 and A[j] > key`

Enquanto houver elemento à esquerda **e** esse elemento for maior que `key`:

```python
A[j + 1] = A[j]   # empurra o elemento maior uma casa para a direita
j = j - 1         # olha o próximo à esquerda
```

- Os elementos maiores que `key` andam uma casa para a direita, abrindo espaço.
- A condição `j >= 0` vem **primeiro** de propósito. O `and` do Python para na primeira condição falsa. Se `j` for `-1`, o `A[j]` nem é avaliado. Se a ordem fosse inversa, `A[-1]` seria lido, e em Python isso é o **último** elemento da lista, sem erro nenhum, o que daria um resultado errado.

### 5. Colocar a chave: `A[j + 1] = key`

Quando o laço interno para, `j + 1` é a posição certa:

- Ou `j` passou do início (`j = -1`), então `key` é o menor de todos e vai para a posição 0.
- Ou `A[j] <= key`, então `key` vai logo depois de `A[j]`.

## Exemplo completo

`A = [5, 2, 4, 6, 1, 3]`, `n = 6`.

| `i` | `key` | Deslocamentos | `A` depois |
|---|---|---|---|
| início | | | `[5, 2, 4, 6, 1, 3]` |
| 1 | 2 | `5` vai para a direita | `[2, 5, 4, 6, 1, 3]` |
| 2 | 4 | `5` vai para a direita | `[2, 4, 5, 6, 1, 3]` |
| 3 | 6 | nenhum (`5 > 6` é falso) | `[2, 4, 5, 6, 1, 3]` |
| 4 | 1 | `6`, `5`, `4` e `2` vão para a direita | `[1, 2, 4, 5, 6, 3]` |
| 5 | 3 | `6`, `5` e `4` vão para a direita | `[1, 2, 3, 4, 5, 6]` |

## Zoom no `i = 4`

`key = 1`, `j = 3`. Este é o passo com mais deslocamentos. Repare que há sempre uma posição "duplicada", que é a vaga aberta para `key`:

| Etapa | `j` | Teste `A[j] > 1` | `A` depois |
|---|---|---|---|
| início | 3 | `6 > 1` ✔ | `[2, 4, 5, 6, 6, 3]` (`A[4] = A[3]`) |
| | 2 | `5 > 1` ✔ | `[2, 4, 5, 5, 6, 3]` (`A[3] = A[2]`) |
| | 1 | `4 > 1` ✔ | `[2, 4, 4, 5, 6, 3]` (`A[2] = A[1]`) |
| | 0 | `2 > 1` ✔ | `[2, 2, 4, 5, 6, 3]` (`A[1] = A[0]`) |
| | -1 | `j >= 0` falso, para | |
| coloca | | `A[j+1] = A[0] = key` | `[1, 2, 4, 5, 6, 3]` |

O `1` original em `A[4]` foi sobrescrito pelo `6`. Ele não se perdeu porque estava salvo em `key`. É por isso que o passo 2 existe.

## Os três cenários do arquivo

O que muda entre eles é quantas vezes o laço interno executa:

| Cenário | Entrada | Laço interno | Custo |
|---|---|---|---|
| Melhor | já ordenado: `[1, 2, ..., 10]` | nunca executa, só uma comparação por `i` | Θ(n) |
| Médio | ordem aleatória: `[7, 3, 10, 1, 5, ...]` | cada elemento anda, em média, metade do caminho | Θ(n²) |
| Pior | ordem inversa: `[10, 9, ..., 1]` | cada elemento anda até o início | Θ(n²) |

No pior caso com `n = 10`, o total é `1 + 2 + ... + 9 = 45` deslocamentos, ou seja, `n(n-1)/2`. Isso cresce com o quadrado de `n`.

## Detalhes importantes

- **`>` e não `>=`:** um elemento igual a `key` **não** é empurrado. Assim, elementos iguais mantêm a ordem original entre si, e a ordenação é **estável**.
- **Em lugar:** só usa `key` e `j` como memória extra, ou seja, Θ(1) de espaço auxiliar. O vetor é alterado no próprio lugar, e `return A` devolve a mesma lista, não uma cópia.
- **Bom para vetores pequenos ou quase ordenados:** quanto mais ordenada a entrada, menos deslocamentos. Em um vetor quase ordenado, o custo fica perto de Θ(n).
- **Invariante do laço:** no início de cada volta do `for`, `A[0..i-1]` contém os mesmos elementos que estavam lá originalmente, mas já ordenados. Ao fim do `for`, com `i = n`, o vetor inteiro está ordenado.
- **Índices:** o comentário `A[1:i-1]` do código vem do pseudocódigo, que conta posições a partir de 1. Em Python as posições começam em 0, então a parte ordenada é `A[0..i-1]`.
