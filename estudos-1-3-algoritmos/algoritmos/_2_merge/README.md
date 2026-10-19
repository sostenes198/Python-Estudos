# Intercalação (MERGE)

Implementação em [`merge.py`](merge.py).

## A ideia

`merge(A, p, q, r)` junta duas partes de `A` que **já estão ordenadas** e deixa o trecho `A[p..r]` inteiro ordenado:

```
        p            q  q+1          r
A = [ ... | parte esquerda | parte direita | ... ]
          |  já ordenada   |  já ordenada  |
```

- **Parte esquerda:** vai de `p` até `q`.
- **Parte direita:** vai de `q+1` até `r`.
- **Limites inclusivos:** os três índices valem para o pseudocódigo e para o Python. Em Python, a esquerda seria `A[p:q+1]`.

Pense em duas pilhas de cartas, cada uma com a menor carta em cima. Você olha as duas de cima, pega a menor e coloca na mesa. Repete até acabar uma das pilhas. Depois joga o resto da outra por cima.

## Passo a passo do código

### 1. Tamanhos

```python
n_left = q - p + 1   # elementos de p até q
n_right = r - q      # elementos de q+1 até r
```

Com `p=1, q=3, r=5`: `n_left = 3` (posições 1, 2, 3) e `n_right = 2` (posições 4, 5).

### 2. Cópias

```python
L = [0] * n_left
R = [0] * n_right
for i in range(n_left):  L[i] = A[p + i]
for j in range(n_right): R[j] = A[q + j + 1]
```

- **Por que copiar:** o passo seguinte vai escrever de volta em `A`, e isso sobrescreveria elementos que ainda não foram usados. `L` e `R` guardam esses valores.
- **Por que `q + j + 1`:** a direita começa em `q+1`, então o elemento `j` dela está em `A[q+1+j]`.
- **`[0] * n`:** só cria a lista com o tamanho certo. Os zeros são preenchidos logo depois.

### 3. Os três ponteiros

```python
i = 0   # próximo candidato em L
j = 0   # próximo candidato em R
k = p   # próxima posição de A a preencher
```

`i` e `j` andam sobre `L` e `R`, que são cópias e começam em 0. `k` anda sobre `A` e começa em `p`, porque é onde o trecho começa no vetor original.

### 4. O laço principal

```python
while i < n_left and j < n_right:
    if L[i] <= R[j]:
        A[k] = L[i]; i += 1
    else:
        A[k] = R[j]; j += 1
    k += 1
```

A cada volta, o menor entre `L[i]` e `R[j]` vai para `A[k]`. Só o ponteiro de quem "ganhou" avança, e `k` sempre avança.

Como `L` e `R` estão ordenados, o menor de todos os elementos restantes é sempre `L[i]` ou `R[j]`. Por isso basta comparar os dois.

O laço termina quando **uma** das listas acaba.

### 5. Os dois laços de sobra

```python
while i < n_left:  A[k] = L[i]; i += 1; k += 1
while j < n_right: A[k] = R[j]; j += 1; k += 1
```

Quando uma lista acaba, o que sobra na outra já está ordenado e é maior ou igual a tudo que foi colocado. Basta copiar. **No máximo um** desses dois laços executa, porque o laço principal só sai quando uma das listas esgota.

## Exemplo 1: subvetor no meio de `A`

`A = [9, 1, 4, 6, 2, 3, 8, 0]`, chamando `merge(A, 1, 3, 5)`.

Os valores iniciais são:

- `n_left = 3` e `n_right = 2`
- `L = [1, 4, 6]` e `R = [2, 3]`
- `i = 0`, `j = 0` e `k = 1`

O `9` (posição 0) e o `8, 0` (posições 6 e 7) ficam fora e **não são tocados**.

| Passo       | Comparação           | Ação                     | `A` depois                 |
| ----------- | -------------------- | ------------------------ | -------------------------- |
| início      |                      |                          | `[9, 1, 4, 6, 2, 3, 8, 0]` |
| 1           | `L[0]=1 <= R[0]=2` ✔ | `A[1]=1`, `i=1`          | `[9, 1, 4, 6, 2, 3, 8, 0]` |
| 2           | `L[1]=4 <= R[0]=2` ✘ | `A[2]=2`, `j=1`          | `[9, 1, 2, 6, 2, 3, 8, 0]` |
| 3           | `L[1]=4 <= R[1]=3` ✘ | `A[3]=3`, `j=2`          | `[9, 1, 2, 3, 2, 3, 8, 0]` |
| fim do laço | `j == n_right`       | sai do `while` principal |                            |
| sobra 1     | copia `L[1]`         | `A[4]=4`, `i=2`          | `[9, 1, 2, 3, 4, 3, 8, 0]` |
| sobra 2     | copia `L[2]`         | `A[5]=6`, `i=3`          | `[9, 1, 2, 3, 4, 6, 8, 0]` |

No passo 2, `A[2] = 2` sobrescreveu o `4` original. Ele não se perdeu porque estava salvo em `L[1]`. É isso que justifica o passo 2 do código.

## Exemplo 2: sobra na direita

`A = [1, 2, 3, 4]`, `merge(A, 0, 1, 3)`. Aqui `L = [1, 2]` e `R = [3, 4]`.

- `1 <= 3` ✔, então `A[0]=1` e `i=1`.
- `2 <= 3` ✔, então `A[1]=2` e `i=2`.
- `i == n_left`, então o laço principal acaba.
- O segundo laço de sobra copia `3` e `4` para `A[2]` e `A[3]`.

Esse é o caso do melhor cenário do arquivo. O laço principal só consome `L`, e `R` inteiro cai no laço de sobra.

## Exemplo 3: elementos alternados

`A = [1, 3, 5, 7, 2, 4, 6, 8]`, `merge(A, 0, 3, 7)`. Aqui `L = [1, 3, 5, 7]` e `R = [2, 4, 6, 8]`.

Os dois lados se alternam: `1, 2, 3, 4, 5, 6, 7` saem do laço principal, intercalando `L` e `R`. Depois disso `L` acaba e sobra só o `8` de `R`. Esse é o pior cenário do arquivo, com o maior número de comparações (7).

## Detalhes importantes

- **`<=` e não `<`:** quando dois elementos são iguais, o da esquerda sai primeiro. Isso mantém a ordem original entre iguais, ou seja, torna a ordenação **estável**. Com `<`, funcionaria igual, mas deixaria de ser estável.
- **Em lugar, mas com memória extra:** o resultado fica em `A`, e `return A` devolve a mesma lista, não uma cópia. Mas `L` e `R` ocupam Θ(n) de espaço auxiliar, com n = `r - p + 1`.
- **Custo Θ(n):** copiar custa n operações e intercalar custa mais n. Por isso o melhor e o pior cenário só mudam o número de comparações, não a ordem de grandeza.
- **A pré-condição é responsabilidade de quem chama:** se `A[p..q]` ou `A[q+1..r]` não estiverem ordenados, o `merge` não reclama e devolve um resultado errado.

## Para onde isso vai

No **merge sort**, você divide o vetor ao meio, ordena cada metade recursivamente e chama `merge` para juntar. O caso base é um subvetor de 1 elemento, que já está ordenado. Por isso o `merge` é a peça central: toda a "ordenação" está em juntar pedaços já ordenados.
