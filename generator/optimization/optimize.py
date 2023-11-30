###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
from optimizer import Optimizer

import argparse


def parse_optimization_args(parser):
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
        help="The specific seed to generate (uses a random one if not specified)",
    )
    parser.add_argument(
        "-r",
        "--radius",
        default=2 ** 0.5,
        type=float,
        help="Radius of interaction. (default sqrt(2), i.e Union-Jack grid)",
    )

    parser.add_argument(
        "-TTS", "--TTS_bool", action="store_true", help="Evaluate Time To Solution"
    )

    parser.add_argument(
        "-path", "--path_to_save", required=True, type=str, help="Path to save results"
    )

    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=0,
        help="Maximum number of threads for CPLEX",
    )

    parser.add_argument(
        "-rewiring_frac",
        "--rewiring_frac",
        default=0,
        type=int,
        help="Fraction of edges rewired",
    )

    parser.add_argument(
        "-ER",
        "--ER",
        action="store_true",
        help="Generate Erdos–Renyi graphs",
    )

    args = parser.parse_args()
    return args


def main():
    parser = argparse.ArgumentParser(
        prog="optimizer.py",
        description="",
    )
    args = parse_optimization_args(parser)
    opt_result = Optimizer(
        L=args.L,
        seed=args.seed,
        r=args.radius,
        density=args.density,
        TTS_bool=args.TTS_bool,
        threads=args.threads,
        ER=args.ER,
        rewiring_frac=args.rewiring_frac
    ).optimize(args.path_to_save)

    opt_result.store_results()


if __name__ == "__main__":
    main()
