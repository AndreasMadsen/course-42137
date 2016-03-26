
import _setup
from nose.tools import *

import dataset

def test_basic_properties():
    database = dataset.Database.from_id(1)
    assert_equal(database.meta.courses, 30)
    assert_equal(database.meta.rooms, 6)
    assert_equal(database.meta.days, 5)
    assert_equal(database.meta.periods_per_day, 6)
    assert_equal(database.meta.curricula, 14)
    assert_equal(database.meta.constraints, 53)
    assert_equal(database.meta.lecturers, 24)

def test_count_items():
    database = dataset.Database.from_id(1)
    assert_equal(len(database.courses), 30)
    assert_equal(len(database.curricula), 14)
    assert_equal(sum(len(q.courses) for q in database.curricula.values()), 42)
    assert_equal(len(database.rooms), 6)
    assert_equal(len(database.unavailability), 53)
