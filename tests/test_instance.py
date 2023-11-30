###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
# test_instance.py

import json
import pytest
from instance import Instance


@pytest.fixture
def instance():
    """Create a simple MIS instance"""
    inst = Instance(L=5, density=0.5, seed=123, r=1, version="1.0")
    inst.add_node(0, x=0, y=0)
    inst.add_node(1, x=1, y=0)
    inst.add_node(2, x=0, y=1)
    inst.add_node(3, x=1, y=1)
    inst.add_edge(0, 1)
    inst.add_edge(0, 2)
    inst.add_edge(1, 3)
    inst.add_edge(2, 3)
    return inst


def test_name(instance):
    assert instance.name() == "N4_d0.5_s123_r1.0"


def test_json(instance):
    expected = {
        "problem": {
            "type": "mis",
            "meta": {
                "name": "N4_d0.5_s123_r1.0",
                "description": "Unweighted MIS instance on Union Jack Grid",
                "generator": {
                    "name": "generator.py",
                    "version": instance.version,
                },
                "params": {
                    "L": 5,
                    "density": 0.5,
                    "seed": 123,
                    "r": 1.0,
                },
                "size": {
                    "nodes": 4,
                    "edges": 4,
                },
            },
            "edges": [
                {"ids": [0, 1]},
                {"ids": [0, 2]},
                {"ids": [2, 3]},
                {"ids": [1, 3]},
            ],
        }
    }
    assert json.loads(instance.json()) == expected


def test_svg(instance):
    svg = instance.svg()
    # test svg string is not empty
    assert svg
    # test svg string starts with '<svg'
    assert svg.startswith("<svg")


def test_cplex(instance):
    cplex = instance.cplex()
    # test lp string is not empty
    assert cplex
    # test lp string starts with '\'
    assert cplex.startswith("\\")


def test_metis(instance):
    metis = instance.metis()
    # test metis string is not empty
    assert metis
    # test metis string starts with '%'
    assert metis.startswith("%")


def test_pickle(instance, tmp_path):
    filename = tmp_path / "test.pickle"
    instance.pickle(filename)
    # test that file was created
    assert filename.exists()
    # test that the contents of the file can be unpickled
    import pickle

    with open(filename, "rb") as f:
        adj = pickle.load(f)
    assert adj == [[0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 0, 1], [0, 1, 1, 0]]


def test_edgelist(instance):
    expected = "0, 1\n0, 2\n2, 3\n1, 3"
    assert instance.edgelist() == expected
