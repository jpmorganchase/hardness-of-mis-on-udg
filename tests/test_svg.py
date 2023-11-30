###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
# test_svg.py
import pytest
from svg import Svg


def test_render():
    graph = Svg("10")
    graph.add_node({"x": 2, "y": 3})
    graph.add_node({"x": 4, "y": 6})
    graph.add_edge(graph.nodes[0], graph.nodes[1])
    expected_svg = str(graph.render())
    assert graph.render() == expected_svg
