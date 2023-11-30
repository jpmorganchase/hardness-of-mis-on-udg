###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
# test_generator.py

import pytest
from generator import Generator


gn = Generator


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (1, [(-1, 0), (0, -1), (0, 1), (1, 0)]),
        (
            2,
            [
                (-2, 0),
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -2),
                (0, -1),
                (0, 1),
                (0, 2),
                (1, -1),
                (1, 0),
                (1, 1),
                (2, 0),
            ],
        ),
    ],
)
def test_action_with_parametrization(test_input, expected):
    assert gn.generate_all_directions(test_input) == expected
