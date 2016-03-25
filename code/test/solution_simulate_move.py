
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

def test_remove_failure():
    s = solution.Solution(database, list(orignal_schedule))

    # missing
    assert_equal(s.simulate_move((2, 0, 0, 0), (4, 3, 0)), None)
    assert_equal(sorted(s.export()), orignal_schedule)

def test_add_failure():
    s = solution.Solution(database, list(orignal_schedule))

    # Insert course 0 on (4, 0, 0)
    assert_equal(s.simulate_move((0, 0, 0, 0), (4, 0, 0)), None)
    assert_equal(sorted(s.export()), orignal_schedule)

def test_redudant_swap():
    s = solution.Solution(database, list(orignal_schedule))

    # Move course 0 (0, 3, 0), only redundant on an atomic level
    assert_equal(s.simulate_move((0, 0, 0, 0), (0, 3, 0)).cost(), 0)
    assert_equal(sorted(s.export()), orignal_schedule)

def test_working_swap():
    # More working days for course 1
    s = solution.Solution(database, list(orignal_schedule))

    # continuity and workday bonus
    assert_equal(s.simulate_move((1, 4, 2, 0), (1, 1, 0)).dict(), {
        'U_sum': 0,
        'W_sum': -1,
        'P_sum': 0,
        'A_sum': -1,
        'V_sum': 0
    })
    assert_equal(sorted(s.export()), orignal_schedule)
