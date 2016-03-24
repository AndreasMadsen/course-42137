
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

    # Swap left
    assert_equal(s.mutate_swap((2, 1, 0, 0), (1, 4, 2, 0), full=True), {
        'U_sum': 0,
        'W_sum': -1,
        'P_sum': 0,
        'A_sum': 0,
        'V_sum': 0
    })

    # Swap right
    assert_equal(s.mutate_swap((1, 4, 2, 0), (2, 1, 0, 0), full=True), {
        'U_sum': 0,
        'W_sum': 1,
        'P_sum': 0,
        'A_sum': 0,
        'V_sum': 0
    })
    assert_equal(sorted(s.export()), orignal_schedule)
