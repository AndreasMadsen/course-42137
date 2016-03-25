
import _setup
from nose.tools import *

import dataset
import solution

database = dataset.Database.from_id(1)

def total_cost(U_sum, W_sum, A_sum, P_sum, V_sum):
    return 10 * U_sum + 5 * W_sum + 2 * A_sum + P_sum + V_sum

def validate_additions(schedule, expected_penalties):
    # Start with an empty solution
    s = solution.Solution(database)

    # All adds are assumed valid
    for combination in schedule:
        s.mutate_add(*combination)

    # Validate penalties
    assert_equal(s.penalties, expected_penalties)
    assert_equal(s.objective, total_cost(**expected_penalties))

def test_empty_solution():
    # no courses, the solution starts out with a non-zero penalty
    validate_additions([], {
        'A_sum': 0,
        'V_sum': 0,
        'U_sum': 160,
        'W_sum': 106,
        'P_sum': 0
    })

def test_two_different_times_and_rooms():
    # course 0 is assigned to two different times and rooms
    validate_additions([
        # course, day, period, room
        (0, 0, 0, 0),
        (0, 0, 1, 1)
    ], {
        'A_sum': 0,
        'V_sum': 30,
        'U_sum': 158,
        'W_sum': 105,
        'P_sum': 1
    })

def test_two_different_times_but_same_room():
    # course 0 is assigned to two different times but same room
    validate_additions([
        # course, day, period, room
        (0, 0, 0, 0),
        (0, 0, 1, 0)
    ], {
        'A_sum': 0,
        'V_sum': 0,
        'U_sum': 158,
        'W_sum': 105,
        'P_sum': 0
    })

def test_assigned_just_enogth_times():
    # course 0 is assigned just enogth times
    validate_additions([
        # course, day, period, room
        (0, 0, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 2, 0),
        (0, 1, 0, 0),
        (0, 1, 1, 0),
        (0, 1, 2, 0)
    ], {
        'A_sum': 0,
        'V_sum': 0,
        'U_sum': 154,
        'W_sum': 104,
        'P_sum': 0
    })

def test_diffrent_leacher_and_curricula():
    # course 29 and 0 are not taught by the same teacher or part of same curricula
    validate_additions([
        # course, day, period, room
        (29, 0, 0, 0),
        (0, 0, 0, 1)
    ], {
        'A_sum': 4,
        'V_sum': 30,
        'U_sum': 158,
        'W_sum': 104,
        'P_sum': 0
    })

def test_diffrent_courses_same_curricula():
    # course 4 and 5 belong to the same curricula thus they are adjacent
    validate_additions([
        (4, 0, 0, 1),
        (5, 0, 1, 1)
    ], {
        'A_sum': 0,
        'V_sum': 0,
        'U_sum': 158,
        'W_sum': 104,
        'P_sum': 0
    })

def test_different_courses_same_curricula_tm2():
    # course 2 and 3 belong to same curricula, but it is another course at t-2
    validate_additions([
        (2, 3, 0, 0),
        (3, 3, 1, 0),
        (3, 3, 2, 0)
    ], {
        'U_sum': 157,
        'A_sum': 1,
        'P_sum': 0,
        'V_sum': 0,
        'W_sum': 104
    })
