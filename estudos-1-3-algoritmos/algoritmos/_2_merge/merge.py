def merge(A, p, q, r):
    # Precondition: A[p:q] and A[q+1:r] (inclusive bounds) are already sorted.

    n_left = q - p + 1  # size of A[p:q]
    n_right = r - q  # size of A[q+1:r]

    L = [0] * n_left
    R = [0] * n_right

    for i in range(n_left):  # copy A[p:q] into L[0:n_left-1]
        L[i] = A[p + i]

    for j in range(n_right):  # copy A[q+1:r] into R[0:n_right-1]
        R[j] = A[q + j + 1]

    i = 0  # i indexes the smallest remaining element in L
    j = 0  # j indexes the smallest remaining element in R
    k = p  # k indexes the location in A to fill

    # While both L and R have an unmerged element,
    # copy the smaller unmerged element back into A[p:r].
    while i < n_left and j < n_right:
        if L[i] <= R[j]:
            A[k] = L[i]
            i = i + 1
        else:
            A[k] = R[j]
            j = j + 1

        k = k + 1

    # Having gone through one of L or R entirely, copy the rest
    # of the other to the end of A[p:r].
    while i < n_left:
        A[k] = L[i]
        i = i + 1
        k = k + 1

    while j < n_right:
        A[k] = R[j]
        j = j + 1
        k = k + 1

    return A


if __name__ == "__main__":
    print("Intercalação (MERGE)")

    # Best case: every L element is smaller than R, the first while only consumes L -> Θ(n)
    best_case = [1, 2, 3, 4, 5, 6, 7, 8]
    print(f"Melhor cenário - antes:  {best_case}")
    merge(best_case, 0, 3, 7)
    print(f"Melhor cenário - depois: {best_case}")

    # Average case: sorted halves with mixed-up elements -> Θ(n)
    average_case = [1, 4, 6, 9, 2, 3, 7, 8]
    print(f"Cenário OK - antes:  {average_case}")
    merge(average_case, 0, 3, 7)
    print(f"Cenário OK - depois: {average_case}")

    # Worst case: L and R alternate, the first while only ends at the very end -> Θ(n)
    worst_case = [1, 3, 5, 7, 2, 4, 6, 8]
    print(f"Pior cenário - antes:  {worst_case}")
    merge(worst_case, 0, 3, 7)
    print(f"Pior cenário - depois: {worst_case}")

    # Subarray in the middle of A: p, q, r don't need to cover the whole array
    subarray = [9, 1, 4, 6, 2, 3, 8, 0]
    print(f"Subvetor A[1:5] - antes:  {subarray}")
    merge(subarray, 1, 3, 5)
    print(f"Subvetor A[1:5] - depois: {subarray}")
