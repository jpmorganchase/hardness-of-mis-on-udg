###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
from docplex.mp.progress import ProgressListener, ProgressClock
from docplex.mp.model_reader import ModelReader

import time
import os


class BestBoundAborter(ProgressListener):
    """
    Custom aborter to stop when finding a feasible solution matching the bound.
    """

    def __init__(
        self, max_best_bound: float = 0, minimize: bool = False, log_file_obj=None
    ):
        super(BestBoundAborter, self).__init__(ProgressClock.BestBound)
        self.max_best_bound = max_best_bound
        self.last_obj = None
        self.minimize = minimize
        self.log_file_obj = log_file_obj

    def notify_start(self):
        super(BestBoundAborter, self).notify_start()
        self.last_obj = None

    def stopping_condition(self):
        if self.minimize:
            return self.last_obj <= self.max_best_bound
        else:
            return self.last_obj >= self.max_best_bound

    def notify_progress(self, pdata):
        super(BestBoundAborter, self).notify_progress(pdata)
        if pdata.has_incumbent:
            self.last_obj = pdata.current_objective
            if self.stopping_condition():
                msg = f"_____ FOUND Feasible solution {self.last_obj} better than stopping condition {self.max_best_bound}\n"
                if self.log_file_obj:
                    self.log_file_obj.write(msg)
                else:
                    print(msg)
                self.abort()


def run_cplex_once(
    path: str,
    log_file_path: str,
    TTS: bool = True,
    sol_value: float = None,
    threads: int = 0,
):
    """
    Run CPLEX and log results
    Args:
        path: path to lp to be optimized
        log_file_path: path to logs file path
        TTS: is a boolean that when true it calculates first the solution, and then it runs again CPLEX to obtain the TTS by using the class above.
        sol_value: stopping criteria for TTS, should be the optimal solution. If TTS this argument is required
        threads: maximum number of threads to used by CPLEX, for default behavior set to 0
    """
    if (TTS is True) and (sol_value is None):
        raise ValueError("To run TTS one need the target solution (sol_value)")

    print(f"Optimizing with CPLEX {path}, save log in {log_file_path}")
    mdl = ModelReader.read(path, ignore_names=True)
    log_file_obj = open(log_file_path, "w")
    mdl.context.solver.log_output = log_file_obj
    if threads != 0:
        mdl.context.cplex_parameters.threads = threads
    if TTS:
        mdl.add_progress_listener(
            BestBoundAborter(max_best_bound=sol_value, log_file_obj=log_file_obj)
        )
    time_bis = time.time()
    raw_time_start = time.process_time()

    msol = mdl.solve()

    raw_time_end = time.process_time()
    time_end = time.time()

    raw_time_diff = raw_time_end - raw_time_start
    time_diff = time_end - time_bis

    cplex_time = msol.solve_details.time
    sol_value = msol.objective_value
    log_file_obj.close()
    return (
        cplex_time,
        raw_time_diff,
        time_diff,
        int(msol.objective_value),
    )


def run_one_instance(path: str, TTS: bool = True, threads: int = 0):
    """
    Run CPLEX on a lp file, if TTS, we run twice, first to find optimal, then to evaluate it's time to optimal solution.
    Args:
        path: this is the string indicating the lp file to optimize
        TTS: is a boolean that when true it calculates first the solution, and then it runs again CPLEX to obtain the TTS by using the class above.
        threads: number of threads to use
    """

    log_dir = os.path.join(os.path.dirname(path), "logs")
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    name = os.path.basename(path)[:-3]
    log_file_path = os.path.join(log_dir, name + "_cplex.log")

    tto_cplex, raw_time_diff, time_diff, optimal_objective_value = run_cplex_once(
        path, log_file_path=log_file_path, TTS=False, threads=threads
    )
    # if we are required, we calculate the TTS by running one more time
    tts_cplex, raw_time_diff_tts, time_diff_tts = 0, 0, 0
    if TTS:
        log_file_path = os.path.join(log_dir, name + "_TTS" + "_cplex.log")
        tts_cplex, raw_time_diff_tts, time_diff_tts, _ = run_cplex_once(
            path,
            log_file_path=log_file_path,
            TTS=True,
            threads=threads,
            sol_value=optimal_objective_value,
        )

    return (
        tto_cplex,
        raw_time_diff,
        time_diff,
        tts_cplex,
        raw_time_diff_tts,
        time_diff_tts,
        int(optimal_objective_value),
    )
