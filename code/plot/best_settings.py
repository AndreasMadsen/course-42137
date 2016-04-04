
from _setup import results_path

import gridsearch

alns, tabu = gridsearch.Analyse.load(
    results_path('alns.npy'),
    results_path('tabu.npy')
)

print(alns)
print(tabu)
