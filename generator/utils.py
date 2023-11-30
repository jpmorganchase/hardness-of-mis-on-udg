###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
import math


def format_radius(r):
    return math.ceil(r * 1000) / 1000


def generate_all_radius(L_max):
    """
    Generate directions to grid points with the disk of radius r using brute force
    """
    radius = set()
    r_max = 2**0.5 * L_max
    for x in range(-math.floor(r_max), math.floor(r_max) + 1):
        for y in range(-math.floor(r_max), math.floor(r_max) + 1):
            if 0 < x**2 + y**2 <= r_max**2 and x <= L_max and y <= L_max:
                radius.add(format_radius((x**2 + y**2) ** 0.5))
    return radius
