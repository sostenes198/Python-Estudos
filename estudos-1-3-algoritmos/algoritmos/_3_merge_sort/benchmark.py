import random
import sys
import sysconfig
from time import perf_counter

from algoritmos._3_merge_sort.merge_sort import merge_sort
from algoritmos._3_merge_sort.merge_sort_parallel import merge_sort_parallel

N = 200_000
REPEATS = 3


def best_time(sort, data):
    best = float("inf")

    for _ in range(REPEATS):
        A = data[:]
        start = perf_counter()
        sort(A)
        best = min(best, perf_counter() - start)
        assert A == sorted(data)

    return best


def run(title, data):
    print(f"\n{title} (n = {len(data):,}, melhor de {REPEATS})")

    candidates = [
        ("merge_sort do livro (merge_sort.py)", lambda A: merge_sort(A, 0, len(A) - 1)),
        ("paralelo, 1 thread", lambda A: merge_sort_parallel(A, workers=1)),
        ("paralelo, 2 threads", lambda A: merge_sort_parallel(A, workers=2)),
        ("paralelo, 4 threads", lambda A: merge_sort_parallel(A, workers=4)),
        ("paralelo, 8 threads", lambda A: merge_sort_parallel(A, workers=8)),
        ("paralelo, 14 threads", lambda A: merge_sort_parallel(A, workers=14)),
        ("sorted() do Python (Timsort em C)", lambda A: A.sort()),
    ]

    baseline = None

    for name, sort in candidates:
        t = best_time(sort, data)
        baseline = baseline or t
        print(f"  {name:<38} {t * 1000:>9.1f} ms   {baseline / t:>6.1f}x")


if __name__ == "__main__":
    gil = getattr(sys, "_is_gil_enabled", lambda: True)()
    free_threaded = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))

    print(f"Python {sys.version.split()[0]} | GIL ativo: {gil} | build free-threaded: {free_threaded}")

    random.seed(42)

    run("Aleatório", [random.randint(0, 10**9) for _ in range(N)])
    run("Já ordenado", list(range(N)))
    run("Ordem inversa", list(range(N, 0, -1)))
    run("Poucos valores distintos", [random.randint(0, 9) for _ in range(N)])
