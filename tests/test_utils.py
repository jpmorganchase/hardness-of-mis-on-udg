###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
# test_utils.py
import pytest
import utils as Util


@pytest.mark.parametrize(
    "test_input, expected",
    [(1, 1.0), (1.4142135623730951, 1.415), (3.3166247903554, 3.317)],
)
def test_format_radius(test_input, expected):
    assert Util.format_radius(test_input) == expected
