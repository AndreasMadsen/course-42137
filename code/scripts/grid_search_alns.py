
from _setup import results_path
from _grid_search_shared import databases, initalizer

import collections
import pickle

import numpy as np

import gridsearch
import solution
import dataset
import search

alns_parameters = collections.OrderedDict([
    ('update_lambda', [0.8, 0.9, 0.95, 0.99]),
    ('remove', [1, 5])
])

grid = gridsearch.GridSearch(databases, initalizer, time=3 * 60,
                             verbose=True)

alns_results = grid.search(search.ALNS, alns_parameters)
np.save(results_path('alns.npy'), alns_results, allow_pickle=False)
with open(results_path('alns.plk'), 'wb') as f:
    pickle.dump(alns_parameters, f, protocol=pickle.HIGHEST_PROTOCOL)
