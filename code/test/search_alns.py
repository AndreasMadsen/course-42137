
import _setup
from nose.tools import *

import dataset
import solution
import search

database = dataset.Database.from_id(1)

empty_solution = solution.Solution(database, [])
alns = search.ALNS(database, empty_solution)

def test_solution_improved():
    alns.search(2)
    assert alns.solution.objective < empty_solution.objective
