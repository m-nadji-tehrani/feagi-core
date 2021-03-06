# -*- coding: utf-8 -*-

import pytest
from my_sample_proj.skeleton import fib

__author__ = "Mohammad Nadji-Tehrani"
__copyright__ = "Mohammad Nadji-Tehrani"
__license__ = "mit"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
