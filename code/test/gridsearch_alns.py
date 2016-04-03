
import _setup
from nose.tools import *

import collections

import numpy as np

import gridsearch
import solution
import dataset
import search

database = dataset.Database.from_id(1)

def initalizer(database):
    initial_solution = solution.Solution(database)
    solution.initialize(initial_solution)
    return initial_solution

def test_basic_properties():

    grid = gridsearch.GridSearch([database], initalizer, time=0.000001)

    parameters = collections.OrderedDict([
        ('update_lambda', [0.8, 0.9, 0.95, 0.99]),
        ('w_global', [5, 10, 15]),
        ('w_current', [1, 5, 10]),
        ('remove', [1, 5])
    ])

    results = grid.search(search.ALNS, parameters)
    assert_equal(results.shape, (3, 1, 4, 3, 3, 2))
    assert np.all(results > 100)
