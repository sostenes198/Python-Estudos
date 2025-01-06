import random


def generate_random_number(min, max, quantity):
    return [random.randint(min, max) for _ in range(quantity)]


def execute_algorithm(array):
    size_array = len(array)
    for i in range(1, size_array):
        key = array[i]
        # Inserir A[i] no subvetor ordenado A[1: i – 1].
        j = i - 1
        while j >= 0 and array[j] > key:
            array[j + 1] = array[j]
            j = j - 1
        array[j + 1] = key


if __name__ == '__main__':
    array = generate_random_number(1, 100, 5)
    print(f"Array before sorting: {array}")
    execute_algorithm(array)
    print(f"Array after sorting: {array}")
