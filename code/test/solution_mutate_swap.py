
import _setup
from nose.tools import *

import textwrap

import dataset
import solution

database = dataset.Database.from_id(1)
orignal_schedule = sorted([
    # course, day, period, room
    (0, 0, 0, 0),
    (0, 0, 1, 0),
    (0, 0, 2, 0),
    (1, 4, 0, 0),
    (1, 4, 1, 0),
    (1, 4, 2, 0),
    (2, 1, 0, 0)
])

def test_working_swap():
    # More working days for course 1
    s = solution.Solution(database, list(orignal_schedule))
    old_penalties = dict(s.penalties)
    old_objective = s.objective

    # Swap left
    s.mutate_swap((2, 1, 0, 0), (1, 4, 2, 0))
    # Swap right
    s.mutate_swap((2, 4, 2, 0), (1, 1, 0, 0))

    # Expect same schedule
    assert_equal(sorted(s.export()), orignal_schedule)
    assert_equal(s.penalties, old_penalties)
    assert_equal(s.objective, old_objective)
