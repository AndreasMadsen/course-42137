
import _setup
from nose.tools import *

import dataset
import solution

database = dataset.Database.from_id(1)
initial_penalties = {
    'A_sum': 0,
    'V_sum': 0,
    'U_sum': 160,
    'W_sum': 106,
    'P_sum': 0
}

def total_cost(U_sum, W_sum, A_sum, P_sum, V_sum):
    return 10 * U_sum + 5 * W_sum + 2 * A_sum + P_sum + V_sum

def validate_remove(schedule):
    # Start with an empty solution
    s = solution.Solution(database, schedule=schedule)

    # All removes are assumed valid
    for combination in schedule:
        s.mutate_remove(*combination)

    # Validate penalties
    assert_equal(s.penalties, initial_penalties)
    assert_equal(s.objective, total_cost(**initial_penalties))

def test_empty_solution():
    # no courses, the solution starts out with a non-zero penalty
    validate_remove([])

def test_two_different_times_and_rooms():
    # course 0 is assigned to two different times and rooms
    validate_remove([
        # course, day, period, room
        (0, 0, 0, 0),
        (0, 0, 1, 1)
    ])

def test_two_different_times_but_same_room():
    # course 0 is assigned to two different times but same room
    validate_remove([
        # course, day, period, room
        (0, 0, 0, 0),
        (0, 0, 1, 0)
    ])

def test_assigned_just_enogth_times():
    # course 0 is assigned just enogth times
    validate_remove([
        # course, day, period, room
        (0, 0, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 2, 0),
        (0, 1, 0, 0),
        (0, 1, 1, 0),
        (0, 1, 2, 0)
    ])

def test_diffrent_leacher_and_curricula():
    # course 29 and 0 are not taught by the same teacher or part of same curricula
    validate_remove([
        # course, day, period, room
        (29, 0, 0, 0),
        (0, 0, 0, 1)
    ])

def test_diffrent_courses_same_curricula():
    # course 4 and 5 belong to the same curricula thus they are adjacent
    validate_remove([
        (4, 0, 0, 1),
        (5, 0, 1, 1)
    ])

def test_different_courses_same_curricula_tm2():
    # course 2 and 3 belong to same curricula, but it is another course at t-2
    validate_remove([
        (2, 3, 0, 0),
        (3, 3, 1, 0),
        (3, 3, 2, 0)
    ])
