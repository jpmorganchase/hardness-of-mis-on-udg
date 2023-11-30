###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
from csv import writer
import numpy as np


class Result:
    """
    This class is in charge of creating an object with the relevant information to store, and it actually saves it to the path indicated in the params
    """

    def __init__(self, **params: {}) -> None:
        self.__dict__ = params

    def store_results(self):
        List = [
            self.L,
            self.density,
            self.seed,
            self.r,
            np.round(self.tto_cplex, 6),
            np.round(self.raw_time_diff, 6),
            np.round(self.time_diff, 6),
            np.round(self.tts_cplex, 6),
            np.round(self.raw_time_diff_tts, 6),
            np.round(self.time_diff_tts, 6),
            self.sol,
        ]

        with open(self.path, "a") as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(List)
            f_object.close()


class ResultRewired:
    """
    This class is in charge of creating an object with the relevant information to store, and it actually saves it to the path indicated in the params
    """

    def __init__(self, **params: {}) -> None:
        self.__dict__ = params

    def store_results(self):
        List = [
            self.L,
            self.density,
            self.seed,
            self.r,
            self.rewiring_frac,
            np.round(self.tto_cplex, 6),
            np.round(self.raw_time_diff, 6),
            np.round(self.time_diff, 6),
            np.round(self.tts_cplex, 6),
            np.round(self.raw_time_diff_tts, 6),
            np.round(self.time_diff_tts, 6),
            self.sol,
        ]

        with open(self.path, "a") as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(List)
            f_object.close()
