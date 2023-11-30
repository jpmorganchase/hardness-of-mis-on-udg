###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
from networkx import erdos_renyi_graph
import numpy as np
from instance import Instance
import argparse
import random
import os


def generate_ER_graph(L: int, density: float, seed: int):
    if seed is None:
        seed = random.randrange(100000)
    N = np.round(L * L * density).astype(int)
    p = np.round(
        density ** 2, 4
    )  # p set to match in expectation the number of edges of the original graph
    # set a radius even though is does not make sense for ER graphs, would need to refactor Instance
    instance = Instance(L=L, density=density, seed=seed, r=2 ** 0.5, version="0.2")
    random_state = np.random.RandomState(seed)
    graph = erdos_renyi_graph(n=N, p=p, seed=random_state)
    instance.add_networkx_graph(graph)
    return instance


def save_lp_ER_graph(L, density, seed):
    instance = generate_ER_graph(L, density, seed)
    path = os.path.join("instances", f"L{L}", "ER", instance.name())
    with open(f"{path}.lp", "w") as fh:
        print(f"writing {path}.lp (cplex format)")
        fh.write(instance.cplex())


def main():
    parser = argparse.ArgumentParser(
        prog="generate_ER.py",
        description="Generate lp of ER graph instances",
    )

    parser.add_argument("-L", type=int, required=True, help="The size of the lattice")

    parser.add_argument(
        "-d",
        "--density",
        type=float,
        default=0.8,
        help="Portion of the sites that are occupied (default = 0.8)",
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        required=False,
        default=0,
        help="The specific seed to generate (uses a random one if not specified)",
    )
    parser.add_argument(
        "-c",
        "--cplex",
        action="store_true",
        help="A cplex lp formulation of the instance.",
    )
    args = parser.parse_args()

    save_lp_ER_graph(L=args.L, density=args.density, seed=args.seed)


if __name__ == "__main__":
    main()
