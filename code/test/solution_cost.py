
import _setup
from nose.tools import *

import dataset
import solution

database = dataset.Database.from_id(1)

# course 0 is assigned to two different times and rooms
s = solution.Solution(database, [
    # course, day, period, room
    (0, 0, 0, 0),
    (0, 0, 1, 1)
])

assert_equal(s.cost_seperated(), {
    'A_sum': 0,
    'V_sum': 30,
    'U_sum': 158,
    'W_sum': 105,
    'P_sum': 1
})

# course 0 is assigned to two different times but same room
s = solution.Solution(database, [
    # course, day, period, room
    (0, 0, 0, 0),
    (0, 0, 1, 0)
])

assert_equal(s.cost_seperated(), {
    'A_sum': 0,
    'V_sum': 0,
    'U_sum': 158,
    'W_sum': 105,
    'P_sum': 0
})

# course 0 is assigned just enogth times
s = solution.Solution(database, [
    # course, day, period, room
    (0, 0, 0, 0),
    (0, 0, 1, 0),
    (0, 0, 2, 0),
    (0, 1, 0, 0),
    (0, 1, 1, 0),
    (0, 1, 2, 0)
])

assert_equal(s.cost_seperated(), {
    'A_sum': 0,
    'V_sum': 0,
    'U_sum': 154,
    'W_sum': 104,
    'P_sum': 0
})

# course 29 and 0 are not taught by the same teacher or part of same curricula
s = solution.Solution(database, [
    # course, day, period, room
    (29, 0, 0, 0),
    (0, 0, 0, 1)
])

assert_equal(s.cost_seperated(), {
    'A_sum': 4,
    'V_sum': 30,
    'U_sum': 158,
    'W_sum': 104,
    'P_sum': 0
})
