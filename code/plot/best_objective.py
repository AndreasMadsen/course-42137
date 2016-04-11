
from _setup import results_path

import numpy as np
from tabulate import tabulate

import gridsearch

alns = np.load(results_path('alns.npy'))
tabu = np.load(results_path('tabu.npy'))

alns_best = gridsearch.Analyse.best_objective(alns)
tabu_best = gridsearch.Analyse.best_objective(tabu)
all_best = gridsearch.Analyse.best_objective(tabu, alns)

db_ids = list(range(1, 14, 2))

print(tabulate([
    ["Tabu"] + tabu_best,
    ["ALNS"] + alns_best,
    ["both"] + all_best
], headers=['dataset'] + db_ids, tablefmt='latex'))
