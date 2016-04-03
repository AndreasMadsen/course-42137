
import _setup
from nose.tools import *

import collections

import gridsearch
import solution
import dataset

database = dataset.Database.from_id(1)

def initalizer(database):
    initial_solution = solution.Solution(database)
    solution.initialize(initial_solution)
    return initial_solution

def test_basic_properties():
    grid = gridsearch.GridSearch([database], initalizer)

    parameters = collections.OrderedDict([
        ('bool', [True, False]),
        ('ints', [1, 2, 3]),
        ('fixed', ['A'])
    ])

    assert_equal(list(grid.iterate_settings(parameters)), [
        ({'ints': 1, 'bool': True, 'fixed': 'A'}, (0, 0)),
        ({'ints': 2, 'bool': True, 'fixed': 'A'}, (0, 1)),
        ({'ints': 3, 'bool': True, 'fixed': 'A'}, (0, 2)),

        ({'ints': 1, 'bool': False, 'fixed': 'A'}, (1, 0)),
        ({'ints': 2, 'bool': False, 'fixed': 'A'}, (1, 1)),
        ({'ints': 3, 'bool': False, 'fixed': 'A'}, (1, 2))
    ])
