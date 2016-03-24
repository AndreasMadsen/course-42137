
import _setup
from nose.tools import *

import dataset
import solution

database = dataset.Database.from_id(1)

def validate_delta(solution, combination, final):
    before = solution.cost_seperated()
    delta = solution.simulate_add(*combination, full=True)
    assert_equal(delta, {
        "U_sum": final['U_sum'] - before['U_sum'],
        "W_sum": final['W_sum'] - before['W_sum'],
        "A_sum": final['A_sum'] - before['A_sum'],
        "P_sum": final['P_sum'] - before['P_sum'],
        "V_sum": final['V_sum'] - before['V_sum']
    })

def test_assinged_twice_to_time():
    # course 0 is assigned twice to time (0, 0)
    s = solution.Solution(database, [
        # course, day, period, room
        (0, 0, 0, 0)
    ])
    assert_equal(s.valid(), True)
    assert_equal(s.simulate_add(0, 0, 0, 1), None)

def test_bad_assign_time():
    # course 0 can't be assigned at time (4, 0)
    s = solution.Solution(database, [
        # course, day, period, room
    ])
    assert_equal(s.valid(), True)
    assert_equal(s.simulate_add(0, 4, 0, 0), None)

def test_two_different_times_and_rooms():
    # course 0 is assigned to two different times and rooms
    s = solution.Solution(database, [
        # course, day, period, room
        (0, 0, 0, 0)
    ])
    assert_equal(s.valid(), True)
    validate_delta(s, (0, 0, 1, 1), {
        'A_sum': 0,
        'V_sum': 30,
        'U_sum': 158,
        'W_sum': 105,
        'P_sum': 1
    })
    assert_equal(s.simulate_add(0, 0, 1, 1), 17)

def test_same_time_and_room():
    # course 0 and 1 is assigned to the same time and room
    s = solution.Solution(database, [
        # course, day, period, room
        (0, 0, 0, 0)
    ])
    assert_equal(s.valid(), True)
    assert_equal(s.simulate_add(1, 0, 0, 0), None)

def test_different_times_same_room():
    # course 0 is assigned to two different times but same room
    s = solution.Solution(database, [
        # course, day, period, room
        (0, 0, 0, 0)
    ])
    assert_equal(s.valid(), True)
    validate_delta(s, (0, 0, 1, 0), {
        'A_sum': 0,
        'V_sum': 0,
        'U_sum': 158,
        'W_sum': 105,
        'P_sum': 0
    })
    assert_equal(s.simulate_add(0, 0, 1, 0), -14)

def test_too_many_assigned():
    # course 0 is assigned too many times
    s = solution.Solution(database, [
        # course, day, period, room
        (0, 0, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 2, 0),
        (0, 1, 0, 0),
        (0, 1, 1, 0),
        (0, 1, 2, 0)
    ])
    assert_equal(s.valid(), True)
    assert_equal(s.simulate_add(0, 2, 0, 0), None)

def test_just_enogth_times():
    # course 0 is assigned just enogth times
    s = solution.Solution(database, [
        # course, day, period, room
        (0, 0, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 2, 0),
        (0, 1, 0, 0),
        (0, 1, 1, 0)
    ])
    assert_equal(s.valid(), True)
    validate_delta(s, (0, 1, 2, 0), {
        'A_sum': 0,
        'V_sum': 0,
        'U_sum': 154,
        'W_sum': 104,
        'P_sum': 0
    })
    assert_equal(s.simulate_add(0, 1, 2, 0), -10)

def test_same_curricula():
    # course 2 and 1 belong to the same curricula
    s = solution.Solution(database, [
        # course, day, period, room
        (2, 1, 0, 0)
    ])
    assert_equal(s.valid(), True)
    assert_equal(s.simulate_add(1, 1, 0, 1), None)

def test_same_teacher():
    # course 23 and 8 are taught by the same teacher
    s = solution.Solution(database, [
        # course, day, period, room
        (23, 0, 0, 0)
    ])
    assert_equal(s.valid(), True)
    assert_equal(s.simulate_add(8, 0, 0, 1), None)

def test_different_teacher_and_curricula():
    # course 29 and 0 are not taught by the same teacher or part of same curricula
    s = solution.Solution(database, [
        # course, day, period, room
        (29, 0, 0, 0)
    ])
    assert_equal(s.valid(), True)
    validate_delta(s, (0, 0, 0, 1), {
        'A_sum': 4,
        'V_sum': 30,
        'U_sum': 158,
        'W_sum': 104,
        'P_sum': 0
    })
    assert_equal(s.simulate_add(0, 0, 0, 1), 19)

def test_diffrent_courses_same_curricula():
    # course 4 and 5 belong to the same curricula thus they are adjacent
    s = solution.Solution(database, [
        (4, 0, 0, 1)
    ])
    assert_equal(s.valid(), True)
    validate_delta(s, (5, 0, 1, 1), {
        'A_sum': 0,
        'V_sum': 0,
        'U_sum': 158,
        'W_sum': 104,
        'P_sum': 0
    })
    assert_equal(s.simulate_add(5, 0, 1, 1), -17)
