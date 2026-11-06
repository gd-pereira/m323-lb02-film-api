"""Misst die ID-Suche mit Liste und Set."""

import json
from pathlib import Path
import platform
import statistics
from runpy import run_path
import sys
import timeit
from types import SimpleNamespace

BEFORE = '22a3aed3484b274f71ba014a4370f8327c3069c2'
AFTER = '52c24c5a16b46f92d18442b81523c190e8fc63ba'


def load_version(filename):
    path = Path(__file__).resolve().parent / "evidence" / filename
    return SimpleNamespace(**run_path(str(path)))


def measure(module):
    movies = tuple(module.Movie(i, f'Film {i}', 'Drama', 100, 8)
                   for i in range(5000))
    ids = list(range(2500))
    times = timeit.repeat(lambda: module.select_ids(movies, ids), repeat=5, number=3)
    return [value / 3 * 1000 for value in times]


if __name__ == '__main__':
    before = load_version('movie-before.py.txt')
    after = load_version('movie-after.py.txt')
    for ids in ([0, 2, 2, 99], []):
        old_movies = tuple(before.Movie(i, str(i), 'Drama', 100, 8) for i in range(3))
        new_movies = tuple(after.Movie(i, str(i), 'Drama', 100, 8) for i in range(3))
        assert [m.id for m in before.select_ids(old_movies, ids)] == [
            m.id for m in after.select_ids(new_movies, ids)]
    assert before.select_ids((), [1]) == after.select_ids((), [1]) == ()
    old_times, new_times = measure(before), measure(after)
    result = {
        'before_commit': BEFORE, 'after_commit': AFTER,
        'python': platform.python_version(), 'platform': platform.platform(),
        'movies': 5000, 'requested_ids': 2500, 'repeats': 5, 'calls_per_repeat': 3,
        'unit': 'milliseconds_per_call', 'set_build_included': True,
        'before_times': old_times, 'after_times': new_times,
        'before_median': statistics.median(old_times),
        'after_median': statistics.median(new_times),
        'equal_results_checked': True,
        'list_shallow_bytes': sys.getsizeof(list(range(2500))),
        'set_shallow_bytes': sys.getsizeof(set(range(2500))),
    }
    result['speedup'] = result['before_median'] / result['after_median']
    print(json.dumps(result, indent=2))
