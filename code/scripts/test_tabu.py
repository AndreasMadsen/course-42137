
from _setup import results_path
from _test_shared import databases, initalizer

import collections

import numpy as np

import gridsearch
import solution
import dataset
import search

tabu_parameters = collections.OrderedDict([
    ('diversification', [5]),
    ('intensification', [10]),
    ('allow_swap', ['dynamic']),
    ('tabu_limit', [40])
])

grid = gridsearch.GridSearch(databases, initalizer, time=3 * 60, workers=12,
                             trials=5, verbose=True)

tabu_results = grid.search(search.TABU, tabu_parameters)
np.save(results_path('tabu_test.npy'), tabu_results, allow_pickle=False)
