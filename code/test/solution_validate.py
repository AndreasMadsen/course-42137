
import _setup
from nose.tools import *

import dataset
import solution

database = dataset.Database.from_id(1)

# course 0 is assigned twice to time (0, 0)
s = solution.Solution(database, [
    # course, day, period, room
    (0, 0, 0, 0),
    (0, 0, 0, 1)
])
assert_equal(s.valid(), False)

# course 0 can't be assigned at time (4, 0)
s = solution.Solution(database, [
    # course, day, period, room
    (0, 4, 0, 0),
    (0, 4, 0, 0)
])
assert_equal(s.valid(), False)

# course 0 is assigned to two different times and rooms
s = solution.Solution(database, [
    # course, day, period, room
    (0, 0, 0, 0),
    (0, 0, 1, 1)
])
assert_equal(s.valid(), True)

# course 0 and 1 is assigned to the same time and room
s = solution.Solution(database, [
    # course, day, period, room
    (0, 0, 0, 0),
    (1, 0, 0, 0)
])
assert_equal(s.valid(), False)

# course 0 is assigned to two different times but same room
s = solution.Solution(database, [
    # course, day, period, room
    (0, 0, 0, 0),
    (0, 0, 1, 0)
])
assert_equal(s.valid(), True)

# course 0 is assigned too many times
s = solution.Solution(database, [
    # course, day, period, room
    (0, 0, 0, 0),
    (0, 0, 1, 0),
    (0, 0, 2, 0),
    (0, 1, 0, 0),
    (0, 1, 1, 0),
    (0, 1, 2, 0),
    (0, 2, 0, 0)
])
assert_equal(s.valid(), False)

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
assert_equal(s.valid(), True)

# course 2 and 1 belong to the same curricula
s = solution.Solution(database, [
    # course, day, period, room
    (2, 1, 0, 0),
    (1, 1, 0, 1)
])
assert_equal(s.valid(), False)

# course 23 and 8 are taught by the same teacher
s = solution.Solution(database, [
    # course, day, period, room
    (23, 0, 0, 0),
    (8, 0, 0, 1)
])
assert_equal(s.valid(), False)

# course 29 and 0 are not taught by the same teacher or part of same curricula
s = solution.Solution(database, [
    # course, day, period, room
    (29, 0, 0, 0),
    (0, 0, 0, 1)
])
assert_equal(s.valid(), True)

database.close()
