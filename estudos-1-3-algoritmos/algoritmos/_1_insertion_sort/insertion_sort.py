def insertion_sort(A, n):
    for i in range(1, n):
        key = A[i]

        # Insert A[i] into the sorted subarray A[1:i-1]

        j = i - 1

        while j >= 0 and A[j] > key:
            A[j + 1] = A[j]

            j = j - 1

        A[j + 1] = key

    return A


if __name__ == "__main__":
    print("Ordenação por inserção")

    # Best case: already sorted, the while never runs -> Θ(n)
    best_case = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print(f"Melhor cenário - antes:  {best_case}")
    insertion_sort(best_case, len(best_case))
    print(f"Melhor cenário - depois: {best_case}")

    # Average case: random order, each element moves half the way on average -> Θ(n²)
    average_case = [7, 3, 10, 1, 5, 9, 2, 8, 4, 6]
    print(f"Cenário OK - antes:  {average_case}")
    insertion_sort(average_case, len(average_case))
    print(f"Cenário OK - depois: {average_case}")

    # Worst case: reverse order, each element moves all the way to the start -> Θ(n²)
    worst_case = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    print(f"Pior cenário - antes:  {worst_case}")
    insertion_sort(worst_case, len(worst_case))
    print(f"Pior cenário - depois: {worst_case}")
