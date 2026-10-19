from algoritmos._2_merge.merge import merge


def merge_sort(A, p, r):
    # Sorts A[p:r] (inclusive bounds).

    if p >= r:  # zero or one element: already sorted
        return A

    q = (p + r) // 2  # midpoint of A[p:r]

    merge_sort(A, p, q)  # sort A[p:q]
    merge_sort(A, q + 1, r)  # sort A[q+1:r]

    # Merge A[p:q] and A[q+1:r] into A[p:r]
    merge(A, p, q, r)

    return A


if __name__ == "__main__":
    print("Ordenação por intercalação (MERGE-SORT)")

    # Best case: already sorted, merge only consumes the left half -> Θ(n log n)
    best_case = [1, 2, 3, 4, 5, 6, 7, 8]
    print(f"Melhor cenário - antes:  {best_case}")
    merge_sort(best_case, 0, len(best_case) - 1)
    print(f"Melhor cenário - depois: {best_case}")

    # Average case: random order -> Θ(n log n)
    average_case = [5, 2, 4, 7, 1, 3, 2, 6]
    print(f"Cenário OK - antes:  {average_case}")
    merge_sort(average_case, 0, len(average_case) - 1)
    print(f"Cenário OK - depois: {average_case}")

    # Worst case: reverse order, every merge goes through the whole array -> Θ(n log n)
    worst_case = [8, 7, 6, 5, 4, 3, 2, 1]
    print(f"Pior cenário - antes:  {worst_case}")
    merge_sort(worst_case, 0, len(worst_case) - 1)
    print(f"Pior cenário - depois: {worst_case}")

    # Odd size: the halves are not equal
    odd_size = [9, 4, 7, 1, 8]
    print(f"Tamanho ímpar - antes:  {odd_size}")
    merge_sort(odd_size, 0, len(odd_size) - 1)
    print(f"Tamanho ímpar - depois: {odd_size}")
