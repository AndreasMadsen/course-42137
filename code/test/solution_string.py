
import _setup
from nose.tools import *

import textwrap

import dataset
import solution

database = dataset.Database.from_id(1)

def test_to_string():
    s = solution.Solution(database, [
        # course, day, period, room
        (0, 0, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 2, 0),
        (0, 1, 0, 0),
        (0, 1, 1, 0),
        (0, 1, 2, 0)
    ])

    assert_equal(str(s), textwrap.dedent("""\
    Unscheduled 154
    RoomCapacity 0
    MinimumWorkingDays 104
    CurriculumCompactness 0
    RoomStability 0
    Objective 2060
    C0000 0 0 R0000
    C0000 0 1 R0000
    C0000 0 2 R0000
    C0000 1 0 R0000
    C0000 1 1 R0000
    C0000 1 2 R0000
    """))
