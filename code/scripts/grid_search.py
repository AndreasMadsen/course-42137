
from _setup import results_path

import collections
import pickle

import numpy as np

import gridsearch
import solution
import dataset
import search

databases = [
    dataset.Database.from_id(1),
    dataset.Database.from_id(2)
]

def initalizer(database):
    initial_solution = solution.Solution(database)
    solution.initialize(initial_solution)
    return initial_solution

alns_parameters = collections.OrderedDict([
    ('update_lambda', [0.8, 0.9, 0.95, 0.99]),
    ('remove', [1, 5])
])

tabu_parameters = collections.OrderedDict([
    ('diversification', [True, False]),
    ('intensification', [True, False]),
    ('allow_swap', [True, False]),
    ('tabu_limit', [None, 20])
])

grid = gridsearch.GridSearch(databases, initalizer, time=3 * 60,
                             verbose=True)

alns_results = grid.search(search.ALNS, alns_parameters)
np.save(results_path('alns.npy'), alns_results, allow_pickle=False)
with open(results_path('alns.plk'), 'wb') as f:
    pickle.dump(alns_parameters, f, protocol=pickle.HIGHEST_PROTOCOL)

tabu_results = grid.search(search.TABU, tabu_parameters)
np.save(results_path('tabu.npy'), tabu_results, allow_pickle=False)
with open(results_path('tabu.plk'), 'wb') as f:
    pickle.dump(tabu_parameters, f, protocol=pickle.HIGHEST_PROTOCOL)
