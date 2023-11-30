###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
import os
from run_cplex import run_one_instance
from opt_result import Result, ResultRewired

from instance import Instance
from utils import format_radius


class Optimizer:
    """
    this is the class that controls the optimization with cplex for unweighted MIS instances on Union Jack lattices created by generate.py
    Args:
        L (int): lattice size, 0 < L < 50
        seed (int): the seed used for the instance
        r (float): radius of interaction, two nodes are connected if within distance r, 1 <= r < 10
        density (float): density, 0 < density < 1.0
        TTS_bool (bool): to enable the calculating of Time to Solution.
        threads (int): number of threads for CPLEX to use. 0 let CPLEX choose.
    """

    def __init__(
        self,
        L: int,
        seed: int,
        r: float = 2 ** 0.5,
        density: float = 0.8,
        TTS_bool: bool = False,
        threads: int = 0,
        rewiring_frac: float = 0,
        ER: bool = False,
    ) -> None:
        self.L = L
        self.seed = seed
        self.r = format_radius(r)
        self.density = density
        self.TTS_bool = TTS_bool
        self.threads = threads
        self.rewiring_frac = rewiring_frac
        self.ER = ER

        # here we follow the notation used in generate.py to go and look to the lp file already created
        an_instance = Instance(L=self.L, density=self.density, seed=self.seed, r=self.r, version="0.2")
        for node in range(round(self.L * self.L * self.density)):
            an_instance.add_node(node)
        folder = os.path.join("instances", f"L{self.L}")
        if ER:
            self.path = os.path.join(folder, "ER", an_instance.name() + ".lp")
        elif self.rewiring_frac != 0:
            self.path = os.path.join(
                folder,
                "rewired",
                an_instance.name() + "_rewired" + str(self.rewiring_frac) + ".lp",
            )
        else:
            self.path = os.path.join(folder, an_instance.name() + ".lp")

    def optimize(self, path_to_save):
        """
        Here we run cplex, and we obtain some results that consider relevant for our experiments
        """
        (
            tto_cplex,
            raw_time_diff,
            time_diff,
            tts_cplex,
            raw_time_diff_tts,
            time_diff_tts,
            sol,
        ) = run_one_instance(self.path, TTS=self.TTS_bool, threads=self.threads)
        path = os.path.join("data", "cplex", path_to_save + ".csv")
        if self.rewiring_frac != 0:
            opt_result = ResultRewired(
                L=self.L,
                density=self.density,
                seed=self.seed,
                r=self.r,
                rewiring_frac=self.rewiring_frac,
                tto_cplex=tto_cplex,
                raw_time_diff=raw_time_diff,
                time_diff=time_diff,
                tts_cplex=tts_cplex,
                raw_time_diff_tts=raw_time_diff_tts,
                time_diff_tts=time_diff_tts,
                sol=sol,
                path=path,
            )
        else:
            opt_result = Result(
                L=self.L,
                density=self.density,
                seed=self.seed,
                r=self.r,
                tto_cplex=tto_cplex,
                raw_time_diff=raw_time_diff,
                time_diff=time_diff,
                tts_cplex=tts_cplex,
                raw_time_diff_tts=raw_time_diff_tts,
                time_diff_tts=time_diff_tts,
                sol=sol,
                path=path,
            )

        return opt_result
