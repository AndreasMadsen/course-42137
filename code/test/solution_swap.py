
import _setup
from nose.tools import *

import dataset
import solution

database = dataset.Database.from_id(1)

s = solution.Solution(database, [
    # course, day, period, room
    (0, 0, 0, 0),
    (0, 0, 1, 0),
    (0, 0, 2, 0),
    (1, 1, 0, 0),
    (1, 1, 1, 0),
    (1, 1, 2, 0)
])

# Both are missing
s.swap((3, 0, 0), (2, 0, 0))
assert_equal(s.valid(), True)
assert_equal(str(s), """\
Unscheduled 154
RoomCapacity 0
MinimumWorkingDays 104
CurriculumCompactness 0
RoomStability 0
Objective 2060
C0000 0 0 R0000
C0000 0 1 R0000
C0000 0 2 R0000
C0001 1 0 R0000
C0001 1 1 R0000
C0001 1 2 R0000
""")

# swap to existing
s.swap((0, 0, 0), (1, 0, 0))
assert_equal(s.valid(), True)
assert_equal(str(s), """\
Unscheduled 154
RoomCapacity 0
MinimumWorkingDays 102
CurriculumCompactness 3
RoomStability 0
Objective 2056
C0000 0 1 R0000
C0000 0 2 R0000
C0001 1 1 R0000
C0001 1 2 R0000
C0001 0 0 R0000
C0000 1 0 R0000
""")
s.swap((0, 0, 0), (1, 0, 0))

# only the first combination exists
s.swap((0, 0, 0), (2, 0, 0))
assert_equal(s.valid(), True)
assert_equal(str(s), """\
Unscheduled 154
RoomCapacity 0
MinimumWorkingDays 103
CurriculumCompactness 2
RoomStability 0
Objective 2059
C0000 0 1 R0000
C0000 0 2 R0000
C0001 1 1 R0000
C0001 1 2 R0000
C0001 1 0 R0000
C0000 2 0 R0000
""")
s.swap((0, 0, 0), (2, 0, 0))

# only the last combination exists
s.swap((2, 0, 0), (1, 0, 0))
assert_equal(s.valid(), True)
assert_equal(str(s), """\
Unscheduled 154
RoomCapacity 0
MinimumWorkingDays 103
CurriculumCompactness 1
RoomStability 0
Objective 2057
C0000 0 1 R0000
C0000 0 2 R0000
C0001 1 1 R0000
C0001 1 2 R0000
C0000 0 0 R0000
C0001 2 0 R0000
""")
