###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
"""instance.py: Representation of an unweighted MIS instance."""

__author__ = "Ruben S. Andrist"
__email__ = "randrist@amazon.com"

import json
import networkx as nx

from svg import Svg
from typing import Any, Dict

from utils import format_radius


class Instance(object):
    """Representation of an MIS instance on a Union Jack lattice.

    This class handles rendering the MIS instance into the different formats.
    """

    def __init__(self, **params: Dict[str, Any]) -> None:
        self.__dict__ = params
        self.nodes = {}
        self.edges = set()
        self.r = format_radius(self.r)

    def name(self) -> str:
        return f"N{len(self.nodes)}_d{self.density}_s{self.seed}_r{self.r}"

    def description(self) -> str:
        return "Unweighted MIS instance on Union Jack Grid"

    def add_node(self, id_nb: int, **attrs) -> None:
        self.nodes[id_nb] = attrs

    def add_edge(self, a: int, b: int) -> None:
        self.edges.add((min(a, b), max(a, b)))

    def reset_instance(self) -> None:
        self.nodes = {}
        self.edges = set()

    def json(self) -> str:
        """A json document containing metadata and the list of edges."""
        edges = []
        for e in self.edges:
            a, b = e
            edges += [{"ids": [a, b]}]
        return (
            json.dumps(
                {
                    "problem": {
                        "type": "mis",
                        "meta": {
                            "name": self.name(),
                            "description": self.description(),
                            "generator": {
                                "name": "generator.py",
                                "version": self.version,
                            },
                            "params": {
                                "L": self.L,
                                "density": self.density,
                                "seed": self.seed,
                                "r": self.r,
                            },
                            "size": {
                                "nodes": len(self.nodes),
                                "edges": len(self.edges),
                            },
                        },
                        "edges": edges,
                    }
                }
            )
            + "\n"
        )

    def svg(self) -> str:
        """A vector rendering of the lattice and edges."""
        s = Svg(self.L)
        for nid, node in self.nodes.items():
            s.add_node(node)
        for e in self.edges:
            a = self.nodes[e[0]]
            b = self.nodes[e[1]]
            s.add_edge(a, b)
        return s.render()

    def cplex(self) -> str:
        """A lp formulation of the instance for CPLEX."""
        lp = f"\\ {self.description()}\n"
        lp += f"\\ format: CPLEX lp\n"
        lp += f"\\ generator.py v{self.version}\n"
        lp += f"\\ name={self.name()}\n"

        lp += f"\\\\ params:\n"
        lp += f"\\\\ L={self.L}\n"
        lp += f"\\\\ density={self.density}\n"
        lp += f"\\\\ seed={self.seed}\n"
        lp += f"\\\\ r={self.r}\n"

        lp += "\nMaximize\n"
        lp += "  obj:"
        N = len(self.nodes)
        per_line = 10
        for i, node in enumerate(self.nodes):
            lp += f" x{i}"
            if i < N - 1:
                lp += " +"
                if i % per_line == per_line - 1:
                    lp += "\n      "

        lp += "\n\nSubject To\n"
        for j, e in enumerate(self.edges):
            node_sum = " + ".join([f"x{i}" for i in e])
            lp += f"  e{j}: {node_sum} <= 1\n"
        lp += "\nBinary\n"
        lp += "\n".join([f"  x{i}" for i in self.nodes])
        lp += "\nEnd\n"
        return lp

    def metis(self) -> str:
        """Metis 4.0 format for KaMIS."""
        metis = f"% {self.description()}\n"
        metis += f"% format: METIS 4.0 (metis4.pdf p16 fig.8a)\n"
        metis += f"% generator.py v{self.version}\n"
        metis += f"% name={self.name()}\n"

        metis += f"%\n% params:\n"
        metis += f"%% L={self.L}\n"
        metis += f"%% density={self.density}\n"
        metis += f"%% seed={self.seed}\n"
        metis += f"%% r={self.r}\n"

        metis += "%\n"
        metis += "% NOTE: Metis node ids start at 1!\n%\n"

        metis += f"{len(self.nodes)} {len(self.edges)} 0\n"
        for i in range(len(self.nodes)):
            adj = [sum(e) - i + 1 for e in self.edges if i in e]
            assert len(adj) > 0
            metis += " ".join([str(x) for x in sorted(adj)]) + "\n"
        return metis

    def pickle(self, filename) -> None:
        """Pickled adjacency matrix."""
        N = len(self.nodes)
        adj = [[0] * N for _ in range(N)]
        for a, b in self.edges:
            adj[a][b] = adj[b][a] = 1
        import pickle

        pickle.dump(adj, open(filename, "wb"))

    def edgelist(self) -> str:
        """Edge list format for julia"""
        return "\n".join(map(lambda x: f"{x[0]}, {x[1]}", self.edges))

    def to_networkx_graph(self) -> nx.Graph:
        G = nx.Graph()
        G.add_nodes_from(self.nodes)
        G.add_edges_from(self.edges)
        return G

    def add_networkx_graph(self, graph: nx.Graph):
        for edge in graph.edges:
            self.add_edge(*edge)
        for node in graph.nodes:
            self.add_node(node)
