def orderna_por_insercao(A, n):
    for i in range(1, n):
        key = A[i]

        # Inserir A[i] no subvetor ordenado A[1:i-1]

        j = i - 1

        while j >= 0 and A[j] > key:
            A[j + 1] = A[j]

            j = j - 1

        A[j + 1] = key

    return A


if __name__ == "__main__":
    print("Ordenação por inserção")

    # Melhor cenário: já ordenado, o while nunca executa -> Θ(n)
    melhor_cenario = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print(f"Melhor cenário - antes:  {melhor_cenario}")
    orderna_por_insercao(melhor_cenario, len(melhor_cenario))
    print(f"Melhor cenário - depois: {melhor_cenario}")

    # Cenário OK: ordem aleatória, cada elemento anda em média metade -> Θ(n²)
    cenario_ok = [7, 3, 10, 1, 5, 9, 2, 8, 4, 6]
    print(f"Cenário OK - antes:  {cenario_ok}")
    orderna_por_insercao(cenario_ok, len(cenario_ok))
    print(f"Cenário OK - depois: {cenario_ok}")

    # Pior cenário: ordem inversa, cada elemento anda até o início -> Θ(n²)
    pior_cenario = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    print(f"Pior cenário - antes:  {pior_cenario}")
    orderna_por_insercao(pior_cenario, len(pior_cenario))
    print(f"Pior cenário - depois: {pior_cenario}")
