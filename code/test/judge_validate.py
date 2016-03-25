
import _setup
from nose.tools import *

import dataset
import judge
import solution

database = dataset.Database.from_id(1)

def test_solution_is_correct():
    s = solution.Solution(database, [
        (0, 0, 0, 0),
        (0, 0, 1, 1)
    ])
    v = judge.Validator(database, s)
    assert_equal(v.valid, True)
    assert_equal(v.correct, True)

def test_solution_is_invalid():
    s = solution.Solution(database, [
        (0, 0, 0, 0)
    ])
    s.schedule.append(solution.Combination(0, 4, 0, 0))
    v = judge.Validator(database, s)
    assert_equal(v.valid, False)
    assert_equal(v.correct, False)

def test_solution_is_valid_but_objective_is_incorrect():
    s = solution.Solution(database, [
        (0, 0, 0, 0),
        (0, 0, 1, 1)
    ])
    s.penalties.U_sum = 10
    v = judge.Validator(database, s)
    assert_equal(v.valid, True)
    assert_equal(v.correct, False)
