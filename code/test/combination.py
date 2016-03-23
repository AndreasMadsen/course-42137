
import _setup
from nose.tools import *

import solution

def test_equal():
    a = solution.Combination(0, 0, 0, 0)
    b = solution.Combination(0, 0, 0, 0)
    assert_equal(a, b)

def test_hash():
    a = solution.Combination(0, 0, 0, 0)
    b = solution.Combination(0, 0, 0, 0)
    assert_equal(hash(a), hash(b))

def test_string():
    a = solution.Combination(0, 0, 0, 0)
    assert_equal(str(a), "C0000 0 0 R0000")
