
from _setup import results_path
from _grid_search_shared import databases, initalizer

import collections
import pickle

import numpy as np

import gridsearch
import solution
import dataset
import search

tabu_parameters = collections.OrderedDict([
    ('diversification', [1, 5, None]),
    ('intensification', [2, 10, None]),
    ('allow_swap', ['never', 'always', 'dynamic']),
    ('tabu_limit', [10, 20, 40, None])
])

grid = gridsearch.GridSearch(databases, initalizer, time=3 * 60, workers=12,
                             verbose=True, dry_run=True)

tabu_results = grid.search(search.TABU, tabu_parameters)
np.save(results_path('tabu.npy'), tabu_results, allow_pickle=False)
with open(results_path('tabu.plk'), 'wb') as f:
    pickle.dump(tabu_parameters, f, protocol=pickle.HIGHEST_PROTOCOL)
