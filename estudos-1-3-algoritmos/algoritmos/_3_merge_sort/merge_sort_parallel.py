import os
import sys
from bisect import bisect_right
from concurrent.futures import ThreadPoolExecutor

# Runs with at most this many elements are sorted with binary insertion sort.
INSERTION_CUTOFF = 48

# Below this size, threads cost more than they save: sort sequentially.
PARALLEL_CUTOFF = 1 << 15


def _binary_insertion_sort(a):
    # In place and stable. bisect finds the position in O(log n) and the slice
    # assignment shifts the elements at C speed.
    for i in range(1, len(a)):
        x = a[i]
        pos = bisect_right(a, x, 0, i)

        if pos != i:
            a[pos + 1 : i + 1] = a[pos:i]
            a[pos] = x

    return a


def _merge(a, i, i_end, b, j, j_end):
    # Merges the sorted a[i:i_end] and b[j:j_end] into a NEW list.
    # Stable: on ties, the element of `a` goes first.

    if i == i_end:
        return b[j:j_end]

    if j == j_end:
        return a[i:i_end]

    # Already in order (or entirely reversed): concatenate at C speed.
    if a[i_end - 1] <= b[j]:
        return a[i:i_end] + b[j:j_end]

    if b[j_end - 1] < a[i]:
        return b[j:j_end] + a[i:i_end]

    out = []
    append = out.append

    x = a[i]
    y = b[j]

    # Only the side that just advanced is read again.
    while True:
        if x <= y:
            append(x)
            i += 1

            if i == i_end:
                break

            x = a[i]
        else:
            append(y)
            j += 1

            if j == j_end:
                break

            y = b[j]

    # One of the two is already empty; the other is copied in one go.
    out += a[i:i_end]
    out += b[j:j_end]

    return out


def _sort(a, lo, hi):
    # Sorts a[lo:hi] into a NEW list; `a` is only read, never written.
    # Not sharing anything mutable is what makes this safe to run in threads.

    if hi - lo <= INSERTION_CUTOFF:
        return _binary_insertion_sort(a[lo:hi])

    mid = (lo + hi) // 2

    left = _sort(a, lo, mid)
    right = _sort(a, mid, hi)

    return _merge(left, 0, len(left), right, 0, len(right))


def _co_rank(k, a, b):
    # How many elements of `a` land among the first k elements of merge(a, b)?
    # Binary search, O(log n). Ties go to `a`, matching the stable _merge.

    lo = max(0, k - len(b))
    hi = min(k, len(a))

    while lo < hi:
        i = (lo + hi) // 2
        j = k - i

        if a[i] <= b[j - 1]:
            lo = i + 1
        else:
            hi = i

    return lo


def _split_merge(pool, a, b, parts):
    # Cuts the merge of a and b into `parts` independent pieces. Returns the
    # futures; the caller joins them in order.

    total = len(a) + len(b)
    cuts = [(0, 0)]

    for t in range(1, parts):
        k = total * t // parts
        i = _co_rank(k, a, b)
        cuts.append((i, k - i))

    cuts.append((len(a), len(b)))

    return [
        pool.submit(_merge, a, i0, i1, b, j0, j1)
        for (i0, j0), (i1, j1) in zip(cuts, cuts[1:])
    ]


def _default_workers():
    # Without the GIL the threads run truly in parallel. With the GIL they take
    # turns, so extra threads only add overhead: one worker is the fastest.
    gil_enabled = getattr(sys, "_is_gil_enabled", lambda: True)()

    return 1 if gil_enabled else (os.cpu_count() or 1)


def merge_sort_parallel(A, workers=None, parallel_cutoff=PARALLEL_CUTOFF):
    # Sorts A in place and returns it. Stable.
    #
    # 1. Cuts A into `workers` contiguous chunks and sorts each in its own thread.
    # 2. Merges the sorted chunks two by two, level by level. Each merge is cut
    #    in pieces with _co_rank, so all the threads stay busy even in the last
    #    merge, the one that touches the whole array.

    n = len(A)

    if workers is None:
        workers = _default_workers()

    if workers <= 1 or n < max(parallel_cutoff, 2 * workers):
        A[:] = _sort(A, 0, n)

        return A

    bounds = [n * t // workers for t in range(workers + 1)]

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(_sort, A, lo, hi) for lo, hi in zip(bounds, bounds[1:])
        ]

        runs = [f.result() for f in futures]

        while len(runs) > 1:
            pairs = len(runs) // 2
            parts = max(1, workers // pairs)

            jobs = [
                _split_merge(pool, runs[2 * p], runs[2 * p + 1], parts)
                for p in range(pairs)
            ]

            merged = []

            for job in jobs:
                out = []

                for f in job:
                    out += f.result()

                merged.append(out)

            if len(runs) % 2:  # odd run out goes up to the next level untouched
                merged.append(runs[-1])

            runs = merged

    A[:] = runs[0]

    return A


if __name__ == "__main__":
    print("Ordenação por intercalação com threads")

    # parallel_cutoff=0 forces the threaded path even on a tiny array.
    small = [5, 2, 4, 7, 1, 3, 2, 6, 9, 0, 8, 12, 11, 10, 15, 14, 13, 16, 19, 18]
    print(f"Vetor pequeno - antes:  {small}")
    merge_sort_parallel(small, workers=4, parallel_cutoff=0)
    print(f"Vetor pequeno - depois: {small}")

    # Worker counts that don't divide the array evenly, or aren't a power of two.
    uneven = [9, 4, 7, 1, 8, 3, 6, 2, 5, 0, 10]
    print(f"Tamanho ímpar, 3 threads - antes:  {uneven}")
    merge_sort_parallel(uneven, workers=3, parallel_cutoff=0)
    print(f"Tamanho ímpar, 3 threads - depois: {uneven}")

    # Reverse order: every chunk is reversed, then the runs merge by concatenation.
    reverse = list(range(30, 0, -1))
    print(f"Ordem inversa - antes:  {reverse}")
    merge_sort_parallel(reverse, workers=4, parallel_cutoff=0)
    print(f"Ordem inversa - depois: {reverse}")

    print(f"Threads usadas por padrão aqui: {_default_workers()}")
    print("Veja o benchmark.py para os tempos.")
