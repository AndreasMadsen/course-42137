
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

    # missing, right failure
    assert_equal(s.simulate_swap((2, 0, 0, 0), (1, 4, 0, 0)), None)
    assert_equal(sorted(s.export()), orignal_schedule)

    # missing, left failure
    assert_equal(s.simulate_swap((1, 4, 0, 0), (2, 0, 0, 0)), None)
    assert_equal(sorted(s.export()), orignal_schedule)

def test_add_failure():
    s = solution.Solution(database, list(orignal_schedule))

    # Insert course 0 on (4, 0, 0), left failure
    assert_equal(s.simulate_swap((0, 0, 0, 0), (1, 4, 0, 0)), None)
    assert_equal(sorted(s.export()), orignal_schedule)

    # Insert course 0 on (4, 0, 0), right failure
    assert_equal(s.simulate_swap((1, 4, 0, 0), (0, 0, 0, 0)), None)
    assert_equal(sorted(s.export()), orignal_schedule)

def test_redudant_swap():
    s = solution.Solution(database, list(orignal_schedule))

    # Swap course 0 with 0 should work but be redundant
    assert_equal(s.simulate_swap((0, 0, 0, 0), (0, 0, 1, 0)).cost(), 0)
    assert_equal(sorted(s.export()), orignal_schedule)

def test_working_swap():
    # More working days for course 1
    s = solution.Solution(database, list(orignal_schedule))

    # Swap left
    assert_equal(s.simulate_swap((2, 1, 0, 0), (1, 4, 2, 0)).dict(), {
        'U_sum': 0,
        'W_sum': -1,
        'P_sum': 0,
        'A_sum': 0,
        'V_sum': 0
    })
    assert_equal(sorted(s.export()), orignal_schedule)

    # Swap right
    assert_equal(s.simulate_swap((1, 4, 2, 0), (2, 1, 0, 0)).dict(), {
        'U_sum': 0,
        'W_sum': -1,
        'P_sum': 0,
        'A_sum': 0,
        'V_sum': 0
    })
    assert_equal(sorted(s.export()), orignal_schedule)
