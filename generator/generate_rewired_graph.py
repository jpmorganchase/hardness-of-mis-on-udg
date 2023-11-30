###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
import random
import os

from instance import Instance
from generator import Generator


def rewire_edges_from_graph(G, num_edges_to_rewire, list_edges):
    """
    G: networkx graph,
    num_edges_to_rewire: number of edges in graph G to rewire
    list_edges (list): list of the edges to pick randomly to rewire
    """

    for _ in range(num_edges_to_rewire):
        u, v = random.choice(list_edges)
        G.remove_edge(u, v)
        edges_from_u = [v for u, v in G.edges(u)]  # nodes connected to u
        new_node = random.choice(
            [
                node
                for node in list(G.nodes())
                if (node not in [u, v]) and (node not in edges_from_u)
            ]
        )  # we select a new node to connect that is not u, v or any node already connected to u
        G.add_edge(u, new_node)
        list_edges = [
            (node1, node2) for (node1, node2) in list_edges if (node1, node2) != (u, v)
        ]  # update the list of edges that we have not touched yet
    return G


def write_rewired_instance(folder, p, an_instance):
    """
    Args:
        folder (str): folder to save the lp file
        p = the fraction of edges to rewire.

    """
    if not os.path.isdir(folder):
        os.makedirs(folder)

    path = os.path.join(folder, an_instance.name() + f"_rewired{p}")
    with open(f"{path}.lp", "w") as fh:
        print(f"writing {path}.lp (cplex format)")
        fh.write(an_instance.cplex())


def generate_rewired_graph(L, density, r, seed):
    """
    Save lp of rewired graphs
    seed is here overloaded, we do not separate generator seed and rewiring seed
    """
    num_points = 20
    instance = Generator(L=L, density=density, r=r).generate(seed=seed)
    G = instance.to_networkx_graph()
    list_edges = list(G.edges())
    initial_num_edges = len(list_edges)
    remove_fraction_per_step = 1 / num_points  # we go each 5% of the edges
    edges_remove = int(initial_num_edges * remove_fraction_per_step)
    for num in range(num_points):
        print(f"seed {seed} and num_edges {edges_remove}")
        G = rewire_edges_from_graph(G, edges_remove, list_edges)
        list_edges = list(
            set(list_edges) & set(list(G.edges()))
        )  # these are the ones that we have not touched yet
        # num_edges_rewired = initial_num_edges-len(list_edges)
        an_instance = Instance(L=L, density=density, r=r, seed=seed, version="0.2")
        an_instance.add_networkx_graph(G)
        folder = os.path.join("instances", f"L{L}", "rewired")
        write_rewired_instance(folder, num, an_instance)


def main():
    num_seeds = 20
    for seed in range(num_seeds):
        generate_rewired_graph(L=21, density=0.8, r=2 ** 0.5, seed=seed)


if __name__ == "__main__":
    main()
