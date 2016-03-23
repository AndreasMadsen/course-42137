
import _setup
from nose.tools import *

import dataset

def test_basic_properties():
    database = dataset.Database.from_id(1)
    assert_equal(database.courses, 30)
    assert_equal(database.rooms, 6)
    assert_equal(database.days, 5)
    assert_equal(database.periods_per_day, 6)
    assert_equal(database.curricula, 14)
    assert_equal(database.constraints, 53)
    assert_equal(database.lecturers, 24)
    database.close()

def test_count_items():
    database = dataset.Database.from_id(1)
    assert_equal(database.execute('select count(*) from courses').fetchone(), (30, ))
    assert_equal(database.execute('select count(*) from curricula').fetchone(), (14, ))
    assert_equal(database.execute('select count(*) from lecturers').fetchone(), (24, ))
    assert_equal(database.execute('select count(*) from relation').fetchone(), (42, ))
    assert_equal(database.execute('select count(*) from rooms').fetchone(), (6, ))
    assert_equal(database.execute('select count(*) from unavailability').fetchone(), (53, ))
    database.close()
