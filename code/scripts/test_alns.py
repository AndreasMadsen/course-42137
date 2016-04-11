
from _setup import results_path
from _test_shared import databases, initalizer

import collections

import numpy as np

import gridsearch
import solution
import dataset
import search

alns_parameters = collections.OrderedDict([
    ('update_lambda', [0.95]),
    ('w_global', [10]),
    ('w_current', [5]),
    ('remove', [1])
])

grid = gridsearch.GridSearch(databases, initalizer, time=3 * 60, workers=12,
                             trials=5, verbose=True)

alns_results = grid.search(search.ALNS, alns_parameters)
np.save(results_path('alns_test.npy'), alns_results, allow_pickle=False)
