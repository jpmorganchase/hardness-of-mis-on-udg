// SPDX-License-Identifier: Apache-2.0
// Copyright 2023: Amazon Web Services, Inc
#include <string>
using std::string;

#include <iostream>
using std::cout;
using std::endl;

#include "independent_set.h"
#include "simulated_annealing.h"

int main(int argc, char *argv[]) {
  if (argc <= 2) {
    cout << argv[0] << " [file] [mis] [replicas] [steps] [b_min] [b_max]"
         << endl;
    return -1;
  }
  string file = argv[1];
  int mis = atoi(argv[2]);
  int replicas = argc > 3 ? atoi(argv[4]) : 10000;
  int steps = argc > 4 ? atoi(argv[5]) : 32;
  double b_min = argc > 5 ? atof(argv[6]) : 1e1;
  double b_max = argc > 6 ? atof(argv[7]) : 5e3;
  int seed = 0;

  IndependentSet model;
  model.load_instance(file);

  SimulatedAnnealing sa;
  sa.set_target_cost(-mis);
  sa.set_model(&model);
  sa.set_betas(b_min, b_max);
  sa.set_seed(seed);
  sa.run(replicas, steps);
}
